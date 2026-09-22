//! Formatos dos arquivos em `data/` (ver SPEC.md, seção 1).

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Mensagem {
    pub id: u32,
    pub ts: u32,
    pub remetente: String,
    pub texto: String,
    pub chave: String,
    pub golpe_real: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Quadrilha {
    pub chave: String,
    pub no: u32,
    pub laranjas: Vec<u32>,
    pub saque: Vec<u32>,
    pub inicio_ts: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Meta {
    pub n_contas: u32,
    pub n_transacoes: u32,
    pub hubs: Vec<u32>,
    pub quadrilhas: Vec<Quadrilha>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Tx {
    pub origem: u32,
    pub destino: u32,
    pub valor: u32,
    pub ts: u32,
}

/// Localiza `data/` a partir do diretório atual ou do diretório do crate.
pub fn data_dir() -> PathBuf {
    let candidates = [
        PathBuf::from("data"),
        Path::new(env!("CARGO_MANIFEST_DIR")).join("data"),
    ];
    for c in &candidates {
        if c.join("meta.json").exists() {
            return c.clone();
        }
    }
    candidates[1].clone()
}

pub fn read_mensagens(dir: &Path) -> Result<Vec<Mensagem>> {
    let f = fs::File::open(dir.join("mensagens.jsonl")).context("abrindo mensagens.jsonl")?;
    let mut out = Vec::new();
    for line in BufReader::new(f).lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        out.push(serde_json::from_str(&line)?);
    }
    Ok(out)
}

pub fn write_mensagens(dir: &Path, msgs: &[Mensagem]) -> Result<()> {
    let mut w = BufWriter::new(fs::File::create(dir.join("mensagens.jsonl"))?);
    for m in msgs {
        serde_json::to_writer(&mut w, m)?;
        w.write_all(b"\n")?;
    }
    Ok(())
}

pub fn read_chaves(dir: &Path) -> Result<HashMap<String, u32>> {
    let s = fs::read_to_string(dir.join("chaves.json")).context("abrindo chaves.json")?;
    Ok(serde_json::from_str(&s)?)
}

pub fn write_chaves(dir: &Path, chaves: &HashMap<String, u32>) -> Result<()> {
    let ordered: std::collections::BTreeMap<_, _> = chaves.iter().collect();
    fs::write(dir.join("chaves.json"), serde_json::to_string_pretty(&ordered)?)?;
    Ok(())
}

pub fn read_meta(dir: &Path) -> Result<Meta> {
    let s = fs::read_to_string(dir.join("meta.json")).context("abrindo meta.json")?;
    Ok(serde_json::from_str(&s)?)
}

pub fn write_meta(dir: &Path, meta: &Meta) -> Result<()> {
    fs::write(dir.join("meta.json"), serde_json::to_string_pretty(meta)?)?;
    Ok(())
}

/// Lê `transacoes.bin`. Retorna `(n_contas, transações ordenadas por ts)`.
pub fn read_transacoes(dir: &Path) -> Result<(u32, Vec<Tx>)> {
    let bytes = fs::read(dir.join("transacoes.bin")).context("abrindo transacoes.bin")?;
    if bytes.len() < 12 || &bytes[0..4] != b"PIX1" {
        bail!("transacoes.bin: cabeçalho inválido");
    }
    let u32_at = |i: usize| u32::from_le_bytes([bytes[i], bytes[i + 1], bytes[i + 2], bytes[i + 3]]);
    let n_contas = u32_at(4);
    let n_tx = u32_at(8) as usize;
    if bytes.len() != 12 + n_tx * 16 {
        bail!("transacoes.bin: tamanho inconsistente");
    }
    let mut txs = Vec::with_capacity(n_tx);
    for k in 0..n_tx {
        let i = 12 + k * 16;
        txs.push(Tx { origem: u32_at(i), destino: u32_at(i + 4), valor: u32_at(i + 8), ts: u32_at(i + 12) });
    }
    Ok((n_contas, txs))
}

pub fn write_transacoes(dir: &Path, n_contas: u32, txs: &[Tx]) -> Result<()> {
    let mut w = BufWriter::new(fs::File::create(dir.join("transacoes.bin"))?);
    w.write_all(b"PIX1")?;
    w.write_all(&n_contas.to_le_bytes())?;
    w.write_all(&(txs.len() as u32).to_le_bytes())?;
    for t in txs {
        w.write_all(&t.origem.to_le_bytes())?;
        w.write_all(&t.destino.to_le_bytes())?;
        w.write_all(&t.valor.to_le_bytes())?;
        w.write_all(&t.ts.to_le_bytes())?;
    }
    Ok(())
}
