//! CLI de conferência: `trace <chave>` ou `trace --todas`. Imprime o resumo JSON (SPEC.md, seção 3).

use anyhow::{bail, Result};
use pix_race::data;
use pix_race::graph::Graph;
use std::time::Instant;

fn main() -> Result<()> {
    let arg = std::env::args().nth(1).unwrap_or_else(|| "--todas".to_string());
    let dir = data::data_dir();
    let t = Instant::now();
    let (n, txs) = data::read_transacoes(&dir)?;
    let graph = Graph::from_txs(n, &txs);
    drop(txs);
    eprintln!("grafo: {} contas, {} transações, carga {} ms", graph.n, graph.n_edges, t.elapsed().as_millis());
    let chaves = data::read_chaves(&dir)?;
    let meta = data::read_meta(&dir)?;
    let mensagens = data::read_mensagens(&dir)?;

    let alvo: Vec<String> = if arg == "--todas" {
        meta.quadrilhas.iter().map(|q| q.chave.clone()).collect()
    } else {
        vec![arg]
    };
    for chave in alvo {
        let Some(&no) = chaves.get(&chave) else { bail!("chave desconhecida: {chave}") };
        let t0 = mensagens
            .iter()
            .find(|m| m.chave == chave)
            .map(|m| m.ts)
            .or_else(|| meta.quadrilhas.iter().find(|q| q.chave == chave).map(|q| q.inicio_ts - 300))
            .unwrap_or(0);
        let t = Instant::now();
        let tr = graph.trace(no, t0);
        let ms = t.elapsed().as_secs_f64() * 1000.0;
        println!("{}", serde_json::to_string(&tr.resumo(&chave))?);
        let q = meta.quadrilhas.iter().find(|q| q.chave == chave);
        let (lr, la) = q.map(|q| (q.laranjas.len(), q.laranjas.iter().filter(|l| tr.laranjas.contains(l)).count())).unwrap_or((0, 0));
        eprintln!("  {chave}: {} nós, {} arestas, laranjas {} (acertou {la}/{lr}), saque {}, {ms:.1} ms", tr.visitados, tr.arestas_sub, tr.laranjas.len(), tr.saque.len());
    }
    Ok(())
}
