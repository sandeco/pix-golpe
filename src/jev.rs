//! Cliente HTTP do Jev (TypeSafe AI System One). SPEC.md, seção 2.

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::time::Duration;

pub const URL: &str = "https://api.typesafe.ai/v1/systemone";
pub const MODEL: &str = "jev-latest";
pub const USD_POR_TOKEN_ENTRADA: f64 = 0.042 / 1e6;

#[derive(Debug, Clone, Serialize)]
pub struct Decisao {
    pub golpe: f64,
    pub tipo: String,
    pub tipo_confianca: f64,
    pub urgencia: f64,
    pub pede_pix: f64,
    pub tokens_in: u64,
    pub tokens_out: u64,
    pub model: String,
}

impl Decisao {
    pub fn verdict(&self) -> &'static str {
        verdict(self.golpe)
    }
    pub fn cost_usd(&self) -> f64 {
        self.tokens_in as f64 * USD_POR_TOKEN_ENTRADA
    }
}

pub fn verdict(golpe: f64) -> &'static str {
    if golpe >= 0.6 {
        "golpe"
    } else if golpe <= 0.4 {
        "ok"
    } else {
        "revisar"
    }
}

pub fn questions() -> serde_json::Value {
    json!({
        "golpe": {"type":"noul","instructions":"This message is a scam or fraud attempt (impersonation, fake bill, fake bank alert, fake prize, pressure to pay)"},
        "tipo": {"type":"choice","instructions":"What kind of message is this","criteria":{
            "troca_numero":"Someone claims to be a relative with a new phone number asking for money",
            "boleto_falso":"Fake bill or invoice to be paid",
            "falsa_central":"Fake bank or support center alert about the account",
            "premio":"Fake prize, lottery or giveaway",
            "pix_errado":"Claims a Pix was sent by mistake and asks for a refund",
            "cobranca_legitima":"Legitimate charge, bill or order confirmation",
            "pessoal":"Ordinary personal message between people who know each other",
            "outro":"Something else"}},
        "urgencia": {"type":"score","instructions":"How much time pressure or threat the message applies","criteria":["No time pressure","Some urgency","Extreme urgency, threats or deadlines"]},
        "pede_pix": {"type":"noul","instructions":"The message asks the reader to make a Pix transfer or payment"}
    })
}

#[derive(Deserialize)]
struct Resp {
    model: String,
    answers: Answers,
    usage: Usage,
}
#[derive(Deserialize)]
struct Answers {
    golpe: Noul,
    tipo: Choice,
    urgencia: Score,
    pede_pix: Noul,
}
#[derive(Deserialize)]
struct Noul {
    noul: f64,
}
#[derive(Deserialize)]
struct Choice {
    choice: String,
    confidence: f64,
}
#[derive(Deserialize)]
struct Score {
    score: f64,
}
#[derive(Deserialize)]
struct Usage {
    input_tokens: u64,
    #[serde(default)]
    output_tokens: u64,
}

#[derive(Clone)]
pub struct JevClient {
    http: reqwest::Client,
    api_key: String,
}

impl JevClient {
    pub fn from_env() -> Result<Self> {
        let api_key = std::env::var("TYPESAFE_API_KEY")
            .ok()
            .filter(|k| !k.trim().is_empty())
            .context("TYPESAFE_API_KEY não definida (ver .env na raiz)")?;
        let http = reqwest::Client::builder().timeout(Duration::from_secs(30)).build()?;
        Ok(Self { http, api_key })
    }

    /// Classifica uma mensagem. Faz até 3 tentativas em 429/529.
    pub async fn classificar(&self, remetente: &str, texto: &str) -> Result<Decisao> {
        let body = json!({
            "model": MODEL,
            "state": {"remetente": remetente, "mensagem": texto},
            "questions": questions(),
        });
        let mut tentativa = 0u32;
        loop {
            let resp = self
                .http
                .post(URL)
                .bearer_auth(&self.api_key)
                .json(&body)
                .send()
                .await?;
            let status = resp.status().as_u16();
            if status == 200 {
                let r: Resp = resp.json().await?;
                return Ok(Decisao {
                    golpe: r.answers.golpe.noul,
                    tipo: r.answers.tipo.choice,
                    tipo_confianca: r.answers.tipo.confidence,
                    urgencia: r.answers.urgencia.score,
                    pede_pix: r.answers.pede_pix.noul,
                    tokens_in: r.usage.input_tokens,
                    tokens_out: r.usage.output_tokens,
                    model: r.model,
                });
            }
            if (status == 429 || status == 529) && tentativa < 3 {
                tokio::time::sleep(Duration::from_millis(200 * 2u64.pow(tentativa))).await;
                tentativa += 1;
                continue;
            }
            let corpo = resp.text().await.unwrap_or_default();
            bail!("Jev respondeu {status}: {corpo}");
        }
    }
}
