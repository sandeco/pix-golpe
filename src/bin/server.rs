//! Servidor da demo: HTTP + WebSocket + lado Rust (Jev + rastreio). SPEC.md, seção 4.

use anyhow::Result;
use axum::{
    extract::{
        ws::{Message, WebSocket, WebSocketUpgrade},
        State,
    },
    response::{Html, IntoResponse},
    routing::get,
    Router,
};
use futures::{SinkExt, StreamExt};
use pix_race::data::{self, Mensagem, Quadrilha};
use pix_race::graph::Graph;
use pix_race::jev::JevClient;
use serde_json::{json, Value};
use std::collections::{HashMap, HashSet};
use std::path::Path;
use std::sync::atomic::{AtomicU32, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use tokio::sync::{broadcast, mpsc, Semaphore};

const PORTA: u16 = 8080;
const CONCORRENCIA: usize = 8;

struct App {
    graph: Graph,
    mensagens: Vec<Mensagem>,
    chaves: HashMap<String, u32>,
    truth: HashMap<u32, Quadrilha>,
    jev: JevClient,
    browsers: broadcast::Sender<String>,
    worker: Mutex<Option<mpsc::UnboundedSender<String>>>,
    rust_status: Mutex<Value>,
    python_status: Mutex<Value>,
    run_id: AtomicU32,
    /// Pausa por mensagem em cada lado (ms). 0 = normal, sem espera.
    pace_ms: AtomicU64,
    /// Vereditos da corrida atual, por lado e id, para o relatório de acurácia.
    verdicts: Mutex<HashMap<String, HashMap<u32, String>>>,
    trace_lock: tokio::sync::Mutex<()>,
    data_dir: String,
    step_ms: u64,
}

#[derive(Default)]
struct Stats {
    decision_ms: Vec<f64>,
    trace_ms: Vec<f64>,
    golpes: u64,
    erros: u64,
    cost_usd: f64,
}

fn percentil(v: &[f64], p: f64) -> f64 {
    if v.is_empty() {
        return 0.0;
    }
    let mut s = v.to_vec();
    s.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let idx = ((p / 100.0) * (s.len() - 1) as f64).round() as usize;
    s[idx]
}

impl App {
    fn to_browsers(&self, v: &Value) {
        let _ = self.browsers.send(v.to_string());
    }
    fn to_worker(&self, v: &Value) {
        if let Some(tx) = self.worker.lock().unwrap().as_ref() {
            let _ = tx.send(v.to_string());
        }
    }
    fn to_all(&self, v: &Value) {
        self.to_browsers(v);
        self.to_worker(v);
    }

    fn registrar_verdict(&self, side: &str, id: u32, verdict: &str) {
        self.verdicts.lock().unwrap().entry(side.to_string()).or_default().insert(id, verdict.to_string());
    }

    /// Matriz de confusão por lado: linhas = real (golpe/normal), colunas = veredito (golpe/ok/revisar).
    fn relatorio(&self) -> Value {
        let verdicts = self.verdicts.lock().unwrap();
        let mut sides = serde_json::Map::new();
        for side in ["rust", "python"] {
            let vs = verdicts.get(side).cloned().unwrap_or_default();
            let mut m = HashMap::<(&str, &str), u64>::new();
            for msg in &self.mensagens {
                let Some(v) = vs.get(&msg.id) else { continue };
                let real = if msg.golpe_real { "golpe" } else { "normal" };
                let pred = match v.as_str() { "golpe" => "golpe", "ok" => "ok", _ => "revisar" };
                *m.entry((real, pred)).or_insert(0) += 1;
            }
            let g = |r, p| m.get(&(r, p)).copied().unwrap_or(0);
            let (tp, fn_, fp, tn) = (g("golpe", "golpe"), g("golpe", "ok") + g("golpe", "revisar"), g("normal", "golpe"), g("normal", "ok") + g("normal", "revisar"));
            let total = vs.len() as u64;
            let div = |a: u64, b: u64| if b == 0 { 0.0 } else { a as f64 / b as f64 };
            sides.insert(side.to_string(), json!({
                "avaliadas": total,
                "matriz": {
                    "golpe": {"golpe": g("golpe", "golpe"), "revisar": g("golpe", "revisar"), "ok": g("golpe", "ok")},
                    "normal": {"golpe": g("normal", "golpe"), "revisar": g("normal", "revisar"), "ok": g("normal", "ok")}
                },
                "tp": tp, "fp": fp, "fn": fn_, "tn": tn,
                "acuracia": div(tp + tn, total), "precisao": div(tp, tp + fp), "recall": div(tp, tp + fn_),
            }));
        }
        let golpes_reais = self.mensagens.iter().filter(|m| m.golpe_real).count();
        json!({"type":"report","run_id":self.run_id.load(Ordering::SeqCst),"total":self.mensagens.len(),"golpes_reais":golpes_reais,"sides":sides})
    }

    /// Acrescenta `truth` a um evento `trace` de qualquer lado.
    fn enrich_truth(&self, ev: &mut Value) {
        if ev["type"] != "trace" {
            return;
        }
        let ids = |v: &Value| -> HashSet<u32> {
            v.as_array()
                .map(|a| a.iter().filter_map(|x| x.as_u64().map(|n| n as u32)).collect())
                .unwrap_or_default()
        };
        let laranjas = ids(&ev["laranjas"]);
        let saque = ids(&ev["saque"]);
        let no = ev["chave"].as_str().and_then(|c| self.chaves.get(c)).copied();
        let truth = match no.and_then(|n| self.truth.get(&n)) {
            Some(q) => json!({
                "laranjas_reais": q.laranjas.len(),
                "laranjas_acertadas": q.laranjas.iter().filter(|l| laranjas.contains(l)).count(),
                "saque_reais": q.saque.len(),
                "saque_acertadas": q.saque.iter().filter(|s| saque.contains(s)).count(),
            }),
            None => json!({"laranjas_reais": 0, "laranjas_acertadas": 0, "saque_reais": 0, "saque_acertadas": 0}),
        };
        ev["truth"] = truth;
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let _ = dotenvy::dotenv();
    let raiz = Path::new(env!("CARGO_MANIFEST_DIR"));
    let dir = data::data_dir();
    println!("dados: {}", dir.display());

    let t = Instant::now();
    let (n, txs) = data::read_transacoes(&dir)?;
    let graph = Graph::from_txs(n, &txs);
    drop(txs);
    let load_ms = t.elapsed().as_millis() as u64;
    // Memória residente do processo com o grafo montado e o vetor bruto de transações já liberado.
    let memory_mb = memory_stats::memory_stats().map(|m| (m.physical_mem as f64 / 1048576.0 * 10.0).round() / 10.0);
    println!("grafo: {} contas, {} transações, carga {} ms, memória {:?} MB", graph.n, graph.n_edges, load_ms, memory_mb);

    let mensagens = data::read_mensagens(&dir)?;
    let chaves = data::read_chaves(&dir)?;
    let meta = data::read_meta(&dir)?;
    let truth: HashMap<u32, Quadrilha> = meta.quadrilhas.into_iter().map(|q| (q.no, q)).collect();

    let jev = JevClient::from_env()?;
    let t = Instant::now();
    let model = match jev.classificar("teste", "Oi, tudo bem? Aquecimento.").await {
        Ok(d) => {
            println!("jev aquecido: {} em {} ms", d.model, t.elapsed().as_millis());
            d.model
        }
        Err(e) => {
            eprintln!("aviso: aquecimento do Jev falhou: {e}");
            "jev-latest".to_string()
        }
    };

    let step_ms = std::env::var("PIX_STEP_MS").ok().and_then(|s| s.parse().ok()).unwrap_or(2500);
    let (browsers, _) = broadcast::channel(8192);
    let app = Arc::new(App {
        rust_status: Mutex::new(json!({"type":"status","side":"rust","state":"ready","nodes":graph.n,"edges":graph.n_edges,"load_ms":load_ms,"memory_mb":memory_mb,"model":model})),
        python_status: Mutex::new(json!({"type":"status","side":"python","state":"offline"})),
        graph,
        mensagens,
        chaves,
        truth,
        jev,
        browsers,
        worker: Mutex::new(None),
        run_id: AtomicU32::new(0),
        pace_ms: AtomicU64::new(0),
        verdicts: Mutex::new(HashMap::new()),
        trace_lock: tokio::sync::Mutex::new(()),
        data_dir: dir.canonicalize().unwrap_or(dir.clone()).to_string_lossy().trim_start_matches(r"\\?\").replace('\\', "/"),
        step_ms,
    });

    // Sobe o worker Python junto, salvo PIX_NO_WORKER=1.
    let worker_py = raiz.join("py-worker").join("worker.py");
    let mut _filho = None;
    if std::env::var("PIX_NO_WORKER").is_err() && worker_py.exists() {
        match tokio::process::Command::new("python").arg(&worker_py).current_dir(raiz).kill_on_drop(true).spawn() {
            Ok(c) => {
                println!("worker python iniciado (pid {:?})", c.id());
                _filho = Some(c);
            }
            Err(e) => eprintln!("aviso: não consegui iniciar o worker python: {e}"),
        }
    }

    let router = Router::new()
        .route("/", get(index))
        .route("/ws", get(ws_browser))
        .route("/ws/worker", get(ws_worker))
        .with_state(app);
    let listener = tokio::net::TcpListener::bind(("0.0.0.0", PORTA)).await?;
    println!("abra http://localhost:{PORTA}");
    axum::serve(listener, router).await?;
    Ok(())
}

async fn index() -> impl IntoResponse {
    let p = Path::new(env!("CARGO_MANIFEST_DIR")).join("static").join("index.html");
    match std::fs::read_to_string(&p) {
        Ok(s) => Html(s),
        Err(e) => Html(format!("<h1>static/index.html não encontrado</h1><p>{e}</p>")),
    }
}

async fn ws_browser(ws: WebSocketUpgrade, State(app): State<Arc<App>>) -> impl IntoResponse {
    ws.on_upgrade(move |s| handle_browser(s, app))
}

async fn ws_worker(ws: WebSocketUpgrade, State(app): State<Arc<App>>) -> impl IntoResponse {
    ws.on_upgrade(move |s| handle_worker(s, app))
}

async fn handle_browser(socket: WebSocket, app: Arc<App>) {
    let (mut tx, mut rx) = socket.split();
    let mut sub = app.browsers.subscribe();
    let inicial = [app.rust_status.lock().unwrap().clone(), app.python_status.lock().unwrap().clone()];
    for s in inicial {
        if tx.send(Message::Text(s.to_string())).await.is_err() {
            return;
        }
    }
    loop {
        tokio::select! {
            m = sub.recv() => match m {
                Ok(s) => { if tx.send(Message::Text(s)).await.is_err() { break; } }
                Err(broadcast::error::RecvError::Lagged(_)) => continue,
                Err(_) => break,
            },
            m = rx.next() => match m {
                Some(Ok(Message::Text(t))) => comando_browser(&app, &t),
                Some(Ok(Message::Close(_))) | None | Some(Err(_)) => break,
                _ => {}
            }
        }
    }
}

fn comando_browser(app: &Arc<App>, texto: &str) {
    let Ok(v) = serde_json::from_str::<Value>(texto) else { return };
    match v["type"].as_str() {
        Some("start") => {
            let mode = v["mode"].as_str().unwrap_or("step").to_string();
            app.pace_ms.store(pace_de(&mode, app.step_ms), Ordering::SeqCst);
            let run_id = app.run_id.fetch_add(1, Ordering::SeqCst) + 1;
            app.verdicts.lock().unwrap().clear();
            app.to_all(&json!({"type":"reset"}));
            tokio::spawn(run(app.clone(), run_id, mode));
        }
        // Troca de ritmo no meio da corrida: vale a partir da próxima mensagem, nos dois lados.
        Some("pace") => {
            let mode = v["mode"].as_str().unwrap_or("serial").to_string();
            let ms = pace_de(&mode, app.step_ms);
            app.pace_ms.store(ms, Ordering::SeqCst);
            app.to_all(&json!({"type":"pace","run_id":app.run_id.load(Ordering::SeqCst),"mode":mode,"ms":ms}));
        }
        Some("report") => {
            app.to_browsers(&app.relatorio());
        }
        Some("stop") => {
            let run_id = app.run_id.fetch_add(1, Ordering::SeqCst);
            app.to_all(&json!({"type":"stop","run_id":run_id}));
        }
        Some("reset") => {
            app.run_id.fetch_add(1, Ordering::SeqCst);
            app.to_all(&json!({"type":"reset"}));
        }
        _ => {}
    }
}

/// "step" = padrão (PIX_STEP_MS), "step:<ms>" = intervalo pedido, "serial"/"burst" = sem espera.
fn pace_de(mode: &str, padrao: u64) -> u64 {
    match mode.strip_prefix("step") {
        Some(resto) => resto.strip_prefix(':').and_then(|s| s.parse().ok()).unwrap_or(padrao),
        None => 0,
    }
}

async fn run(app: Arc<App>, run_id: u32, mode: String) {
    let total = app.mensagens.len();
    // Passo a passo e serial: uma decisão por vez (loop de tempo real). Rajada: 8 em voo por lado.
    // "serial" = todas as mensagens enviadas de uma vez, sem espera, processadas uma a uma.
    let concurrency = if mode == "burst" { CONCORRENCIA } else { 1 };
    let pace_ms = app.pace_ms.load(Ordering::SeqCst);
    app.to_all(&json!({"type":"run","run_id":run_id,"mode":mode,"total":total,"concurrency":concurrency,"pace_ms":pace_ms}));
    let sem = Arc::new(Semaphore::new(concurrency));
    let stats = Arc::new(Mutex::new(Stats::default()));
    let mut set = tokio::task::JoinSet::new();
    let inicio = Instant::now();
    for m in app.mensagens.iter() {
        if app.run_id.load(Ordering::SeqCst) != run_id {
            return;
        }
        app.to_all(&json!({"type":"message","run_id":run_id,"id":m.id,"ts":m.ts,"remetente":m.remetente,"texto":m.texto,"chave":m.chave}));
        set.spawn(processar(app.clone(), run_id, m.clone(), stats.clone(), sem.clone()));
    }
    while set.join_next().await.is_some() {}
    if app.run_id.load(Ordering::SeqCst) != run_id {
        return;
    }
    let s = stats.lock().unwrap();
    app.to_browsers(&json!({
        "type":"done","side":"rust","run_id":run_id,
        "totals":{
            "messages": total, "golpes": s.golpes, "erros": s.erros,
            "decision_p50_ms": percentil(&s.decision_ms, 50.0), "decision_p95_ms": percentil(&s.decision_ms, 95.0),
            "trace_p50_ms": percentil(&s.trace_ms, 50.0), "trace_p95_ms": percentil(&s.trace_ms, 95.0),
            "cost_usd": s.cost_usd, "total_ms": inicio.elapsed().as_millis() as u64,
        }
    }));
}

async fn processar(app: Arc<App>, run_id: u32, m: Mensagem, stats: Arc<Mutex<Stats>>, sem: Arc<Semaphore>) {
    let permit = sem.acquire().await.unwrap();
    let t = Instant::now();
    let res = app.jev.classificar(&m.remetente, &m.texto).await;
    let decision_ms = t.elapsed().as_secs_f64() * 1000.0;
    if app.run_id.load(Ordering::SeqCst) != run_id {
        return;
    }
    let d = match res {
        Ok(d) => d,
        Err(e) => {
            stats.lock().unwrap().erros += 1;
            app.to_browsers(&json!({"type":"error","side":"rust","run_id":run_id,"id":m.id,"message":e.to_string()}));
            return;
        }
    };
    let verdict = d.verdict();
    let cost = d.cost_usd();
    app.registrar_verdict("rust", m.id, verdict);
    {
        let mut s = stats.lock().unwrap();
        s.decision_ms.push(decision_ms);
        s.cost_usd += cost;
        if verdict == "golpe" {
            s.golpes += 1;
        }
    }
    app.to_browsers(&json!({
        "type":"decision","side":"rust","run_id":run_id,"id":m.id,"latency_ms":decision_ms,
        "golpe":d.golpe,"tipo":d.tipo,"tipo_confianca":d.tipo_confianca,"urgencia":d.urgencia,"pede_pix":d.pede_pix,
        "verdict":verdict,"tokens_in":d.tokens_in,"tokens_out":d.tokens_out,"cost_usd":cost,"model":d.model
    }));
    // Ritmo narrado: segura a vez por alguns segundos antes da próxima mensagem deste lado.
    let pace = app.pace_ms.load(Ordering::SeqCst);
    if pace > 0 {
        tokio::time::sleep(Duration::from_millis(pace)).await;
    }
    drop(permit);
    if verdict != "golpe" {
        return;
    }
    let Some(&no) = app.chaves.get(&m.chave) else { return };
    let t0 = m.ts;
    let guard = app.trace_lock.lock().await;
    let app2 = app.clone();
    let (tr, trace_ms) = tokio::task::spawn_blocking(move || {
        let t = Instant::now();
        let tr = app2.graph.trace(no, t0);
        (tr, t.elapsed().as_secs_f64() * 1000.0)
    })
    .await
    .unwrap();
    drop(guard);
    if app.run_id.load(Ordering::SeqCst) != run_id {
        return;
    }
    stats.lock().unwrap().trace_ms.push(trace_ms);
    let (nodes, edges) = tr.para_desenho();
    let mut ev = json!({
        "type":"trace","side":"rust","run_id":run_id,"id":m.id,"chave":m.chave,"latency_ms":trace_ms,
        "visitados":tr.visitados,"arestas_sub":tr.arestas_sub,"laranjas":tr.laranjas,"saque":tr.saque,
        "nodes":nodes.iter().map(|&(v,p,s)| json!([v,p,(s*1000.0).round()/1000.0])).collect::<Vec<_>>(),
        "edges":edges,
    });
    app.enrich_truth(&mut ev);
    app.to_browsers(&ev);
}

async fn handle_worker(socket: WebSocket, app: Arc<App>) {
    let (mut tx, mut rx) = socket.split();
    let (wtx, mut wrx) = mpsc::unbounded_channel::<String>();
    let wtx_ref = wtx.clone();
    *app.worker.lock().unwrap() = Some(wtx);
    let hello = json!({"type":"hello","data_dir":app.data_dir});
    if tx.send(Message::Text(hello.to_string())).await.is_err() {
        return;
    }
    let st = json!({"type":"status","side":"python","state":"connected"});
    *app.python_status.lock().unwrap() = st.clone();
    app.to_browsers(&st);
    println!("worker python conectado");
    loop {
        tokio::select! {
            m = wrx.recv() => match m {
                Some(s) => { if tx.send(Message::Text(s)).await.is_err() { break; } }
                None => break,
            },
            m = rx.next() => match m {
                Some(Ok(Message::Text(t))) => {
                    if let Ok(mut v) = serde_json::from_str::<Value>(&t) {
                        v["side"] = json!("python");
                        if v["type"] == "status" {
                            *app.python_status.lock().unwrap() = v.clone();
                        }
                        if v["type"] == "decision" {
                            if let (Some(id), Some(verdict)) = (v["id"].as_u64(), v["verdict"].as_str()) {
                                app.registrar_verdict("python", id as u32, verdict);
                            }
                        }
                        app.enrich_truth(&mut v);
                        app.to_browsers(&v);
                    }
                }
                Some(Ok(Message::Close(_))) | None | Some(Err(_)) => break,
                _ => {}
            }
        }
    }
    // Só limpa o slot se ainda for o nosso canal (um worker novo pode ter assumido).
    let era_nosso = {
        let mut slot = app.worker.lock().unwrap();
        match slot.as_ref() {
            Some(tx) if tx.same_channel(&wtx_ref) => {
                *slot = None;
                true
            }
            _ => false,
        }
    };
    if era_nosso {
        let st = json!({"type":"status","side":"python","state":"offline"});
        *app.python_status.lock().unwrap() = st.clone();
        app.to_browsers(&st);
    }
    println!("worker python desconectado");
}
