//! Grafo de transações e algoritmo de rastreio (SPEC.md, seção 3).
//! O porte Python em `py-worker/trace.py` deve produzir exatamente a mesma saída.

use crate::data::Tx;
use serde::Serialize;
use std::collections::{HashMap, HashSet, VecDeque};

pub const JANELA: u32 = 86_400;
pub const PROF_MAX: u8 = 5;
pub const VALOR_MIN: u32 = 2_000;
pub const MAX_NOS: usize = 40_000;
pub const ITER_LP: usize = 10;
pub const MAX_NODES_DESENHO: usize = 800;
pub const MAX_EDGES_DESENHO: usize = 1_500;

const NAO_VISITADO: u32 = u32::MAX;

/// Listas de adjacência de saída em formato CSR, ordenadas por ts dentro de cada conta.
pub struct Graph {
    pub n: u32,
    pub n_edges: usize,
    start: Vec<u32>,
    dst: Vec<u32>,
    val: Vec<u32>,
    ts: Vec<u32>,
    pub in_deg: Vec<u32>,
}

impl Graph {
    /// `txs` deve estar ordenado por ts crescente.
    pub fn from_txs(n: u32, txs: &[Tx]) -> Graph {
        let n_us = n as usize;
        let mut count = vec![0u32; n_us + 1];
        let mut in_deg = vec![0u32; n_us];
        for t in txs {
            count[t.origem as usize + 1] += 1;
            in_deg[t.destino as usize] += 1;
        }
        for i in 0..n_us {
            count[i + 1] += count[i];
        }
        let start = count.clone();
        let mut pos = count;
        let mut dst = vec![0u32; txs.len()];
        let mut val = vec![0u32; txs.len()];
        let mut ts = vec![0u32; txs.len()];
        for t in txs {
            let p = pos[t.origem as usize] as usize;
            dst[p] = t.destino;
            val[p] = t.valor;
            ts[p] = t.ts;
            pos[t.origem as usize] += 1;
        }
        Graph { n, n_edges: txs.len(), start, dst, val, ts, in_deg }
    }

    #[inline]
    fn out(&self, v: u32) -> std::ops::Range<usize> {
        self.start[v as usize] as usize..self.start[v as usize + 1] as usize
    }

    /// Soma dos valores de saída na janela e ts da primeira saída (critério do passo A).
    #[inline]
    fn saida_na_janela(&self, v: u32, cv: u32) -> (u64, Option<u32>) {
        let fim = cv + JANELA;
        let mut out_sum: u64 = 0;
        let mut primeiro: Option<u32> = None;
        for i in self.out(v) {
            let ts = self.ts[i];
            if ts < cv {
                continue;
            }
            if ts > fim {
                break;
            }
            if self.val[i] < VALOR_MIN {
                continue;
            }
            out_sum += self.val[i] as u64;
            if primeiro.is_none() {
                primeiro = Some(ts);
            }
        }
        (out_sum, primeiro)
    }

    pub fn trace(&self, no_chave: u32, t0: u32) -> Trace {
        let n = self.n as usize;
        // Vetores densos indexados por id da conta (sentinela = não visitado).
        let mut chegada = vec![NAO_VISITADO; n];
        let mut prof = vec![0u8; n];
        let mut visitados_ord: Vec<u32> = Vec::new();

        // Passo A: expansão temporal
        let mut fila = VecDeque::new();
        let mut sub: Vec<(u32, u32, u32, u32)> = Vec::new();
        chegada[no_chave as usize] = t0;
        visitados_ord.push(no_chave);
        fila.push_back(no_chave);
        while let Some(v) = fila.pop_front() {
            let pv = prof[v as usize];
            if pv == PROF_MAX {
                continue;
            }
            let cv = chegada[v as usize];
            let fim = cv + JANELA;
            for i in self.out(v) {
                let ts = self.ts[i];
                if ts < cv {
                    continue;
                }
                if ts > fim {
                    break;
                }
                let valor = self.val[i];
                if valor < VALOR_MIN {
                    continue;
                }
                let d = self.dst[i];
                sub.push((v, d, valor, ts));
                if chegada[d as usize] == NAO_VISITADO {
                    if visitados_ord.len() >= MAX_NOS {
                        continue;
                    }
                    chegada[d as usize] = ts;
                    prof[d as usize] = pv + 1;
                    visitados_ord.push(d);
                    fila.push_back(d);
                }
            }
        }
        let mut ids = visitados_ord;
        ids.sort_unstable();

        // Passo B: suspeição
        let mut in_sum = vec![0u64; n];
        for &(_, d, valor, _) in &sub {
            in_sum[d as usize] += valor as u64;
        }
        let mut suspeita = vec![0f64; n];
        let mut repasse = vec![0f64; n];
        for &v in &ids {
            if v == no_chave {
                suspeita[v as usize] = 1.0;
                repasse[v as usize] = 1.0;
                continue;
            }
            let cv = chegada[v as usize];
            let (out_sum, primeiro_out) = self.saida_na_janela(v, cv);
            let rep = (out_sum as f64 / in_sum[v as usize] as f64).min(1.0);
            let rapidez = match primeiro_out {
                None => 0.0,
                Some(p) => (1.0 - ((p - cv) as f64) / 3600.0).max(0.0),
            };
            let pequeno = if self.in_deg[v as usize] < 50 { 1.0 } else { 0.0 };
            suspeita[v as usize] = 0.4 * rep + 0.5 * rapidez + 0.1 * pequeno;
            repasse[v as usize] = rep;
        }

        // Passo C: propagação de rótulos (só arestas com os dois extremos visitados)
        let mut pares: Vec<(u32, u32)> = sub
            .iter()
            .filter(|&&(s, d, _, _)| s != d && chegada[d as usize] != NAO_VISITADO)
            .map(|&(s, d, _, _)| (s.min(d), s.max(d)))
            .collect();
        pares.sort_unstable();
        pares.dedup();
        // CSR local de vizinhos, cada lista ordenada por id.
        let mut grau = vec![0u32; n];
        for &(a, b) in &pares {
            grau[a as usize] += 1;
            grau[b as usize] += 1;
        }
        let mut off = vec![0u32; n + 1];
        let mut acc = 0u32;
        for &v in &ids {
            off[v as usize] = acc;
            acc += grau[v as usize];
            off[v as usize + 1] = acc;
        }
        let mut viz = vec![0u32; pares.len() * 2];
        let mut fill = off.clone();
        for &(a, b) in &pares {
            viz[fill[a as usize] as usize] = b;
            fill[a as usize] += 1;
            viz[fill[b as usize] as usize] = a;
            fill[b as usize] += 1;
        }
        for &v in &ids {
            let (s, e) = (off[v as usize] as usize, off[v as usize + 1] as usize);
            viz[s..e].sort_unstable();
        }
        let mut rotulo = vec![0u32; n];
        for &v in &ids {
            rotulo[v as usize] = v;
        }
        let mut contagem: Vec<(u32, f64)> = Vec::with_capacity(16);
        for _ in 0..ITER_LP {
            for &v in &ids {
                let (s, e) = (off[v as usize] as usize, off[v as usize + 1] as usize);
                if s == e {
                    continue;
                }
                contagem.clear();
                for &u in &viz[s..e] {
                    let r = rotulo[u as usize];
                    match contagem.iter_mut().find(|(l, _)| *l == r) {
                        Some(c) => c.1 += suspeita[u as usize],
                        None => contagem.push((r, suspeita[u as usize])),
                    }
                }
                let mut melhor = contagem[0];
                for &(r, soma) in &contagem[1..] {
                    if soma > melhor.1 || (soma == melhor.1 && r < melhor.0) {
                        melhor = (r, soma);
                    }
                }
                rotulo[v as usize] = melhor.0;
            }
        }
        let rc = rotulo[no_chave as usize];

        // Passo D: classificação
        let laranjas: Vec<u32> = ids
            .iter()
            .copied()
            .filter(|&v| v != no_chave && rotulo[v as usize] == rc && suspeita[v as usize] >= 0.6)
            .collect();
        let mut eh_laranja = vec![false; n];
        for &l in &laranjas {
            eh_laranja[l as usize] = true;
        }
        let mut de_laranja = vec![0u32; n];
        for &(s, d, _, _) in &sub {
            if eh_laranja[s as usize] {
                de_laranja[d as usize] += 1;
            }
        }
        let saque: Vec<u32> = ids
            .iter()
            .copied()
            .filter(|&v| v != no_chave && !eh_laranja[v as usize] && de_laranja[v as usize] >= 3 && repasse[v as usize] < 0.3)
            .collect();

        let mut soma = 0.0f64;
        for &v in &ids {
            soma += suspeita[v as usize];
        }
        let soma_suspeita = (soma * 10_000.0).round() / 10_000.0;

        let nos: Vec<(u32, u8, f64)> = ids.iter().map(|&v| (v, prof[v as usize], suspeita[v as usize])).collect();

        Trace {
            no: no_chave,
            t0,
            visitados: ids.len(),
            arestas_sub: sub.len(),
            laranjas,
            saque,
            soma_suspeita,
            nos,
            sub,
        }
    }
}

#[derive(Debug, Clone)]
pub struct Trace {
    pub no: u32,
    pub t0: u32,
    pub visitados: usize,
    pub arestas_sub: usize,
    pub laranjas: Vec<u32>,
    pub saque: Vec<u32>,
    pub soma_suspeita: f64,
    /// (id, prof, suspeita) de todos os nós de chegada, ordenado por id.
    pub nos: Vec<(u32, u8, f64)>,
    /// Arestas (src, dst, valor, ts) na ordem em que a expansão as encontrou.
    pub sub: Vec<(u32, u32, u32, u32)>,
}

/// Resumo para conferência de igualdade com o porte Python.
#[derive(Debug, Serialize)]
pub struct TraceResumo<'a> {
    pub chave: &'a str,
    pub no: u32,
    pub t0: u32,
    pub visitados: usize,
    pub arestas_sub: usize,
    pub laranjas: &'a [u32],
    pub saque: &'a [u32],
    pub soma_suspeita: f64,
}

impl Trace {
    pub fn resumo<'a>(&'a self, chave: &'a str) -> TraceResumo<'a> {
        TraceResumo {
            chave,
            no: self.no,
            t0: self.t0,
            visitados: self.visitados,
            arestas_sub: self.arestas_sub,
            laranjas: &self.laranjas,
            saque: &self.saque,
            soma_suspeita: self.soma_suspeita,
        }
    }

    /// Seleção de nós e arestas para o canvas (SPEC.md, seção 4).
    pub fn para_desenho(&self) -> (Vec<(u32, u8, f64)>, Vec<(u32, u32)>) {
        let info: HashMap<u32, (u8, f64)> = self.nos.iter().map(|&(v, p, s)| (v, (p, s))).collect();
        let especiais: HashSet<u32> = std::iter::once(self.no)
            .chain(self.laranjas.iter().copied())
            .chain(self.saque.iter().copied())
            .collect();
        let mut nodes: Vec<(u32, u8, f64)> = Vec::new();
        let push = |v: u32, nodes: &mut Vec<(u32, u8, f64)>| {
            let (p, s) = info[&v];
            nodes.push((v, p, s));
        };
        push(self.no, &mut nodes);
        for &v in &self.laranjas {
            push(v, &mut nodes);
        }
        for &v in &self.saque {
            push(v, &mut nodes);
        }
        let mut resto: Vec<(u8, u32)> = self
            .nos
            .iter()
            .filter(|(v, _, _)| !especiais.contains(v))
            .map(|&(v, p, _)| (p, v))
            .collect();
        resto.sort_unstable();
        for (_, v) in resto {
            if nodes.len() >= MAX_NODES_DESENHO {
                break;
            }
            push(v, &mut nodes);
        }
        let presentes: HashSet<u32> = nodes.iter().map(|n| n.0).collect();
        let mut vistos: HashSet<(u32, u32)> = HashSet::new();
        let mut prioritarias = Vec::new();
        let mut demais = Vec::new();
        for &(s, d, _, _) in &self.sub {
            if !presentes.contains(&s) || !presentes.contains(&d) || !vistos.insert((s, d)) {
                continue;
            }
            if especiais.contains(&s) || especiais.contains(&d) {
                prioritarias.push((s, d));
            } else {
                demais.push((s, d));
            }
        }
        let mut edges = prioritarias;
        for e in demais {
            if edges.len() >= MAX_EDGES_DESENHO {
                break;
            }
            edges.push(e);
        }
        edges.truncate(MAX_EDGES_DESENHO);
        (nodes, edges)
    }
}
