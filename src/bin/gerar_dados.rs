//! Gera `data/`: mensagens, chaves, transações e verdade de referência. Semente fixa.

use anyhow::Result;
use pix_race::data::{self, Mensagem, Meta, Quadrilha, Tx};
use rand::prelude::*;
use rand_chacha::ChaCha8Rng;
use rand_distr::LogNormal;
use std::collections::{HashMap, HashSet};
use std::path::Path;

const N_CONTAS: u32 = 1_000_000;
const N_HUBS: u32 = 2_000;
const DIAS: u32 = 10;
const N_TX_NORMAIS: usize = 9_500_000;
const N_QUADRILHAS: usize = 40;
const N_MSG_GOLPE: usize = 75;
const N_MSG_LEGIT: usize = 925;

const GOLPES: &[&str] = &[
    "Oi {parente}, troquei de número. Esse é o novo, salva aí. Preciso de um favor: faz um Pix de R$ {valor} pra chave {chave}? Amanhã te devolvo.",
    "{parente}, é o {nome}. Meu celular quebrou e tô usando esse número. Consegue me emprestar R$ {valor}? Pix na chave {chave}, é urgente.",
    "Mãe, sou eu. Perdi o celular e esse é meu número novo. Preciso pagar uma conta HOJE, manda R$ {valor} no Pix {chave} por favor",
    "{banco}: detectamos uma compra suspeita de R$ {valor} no seu cartão. Se não reconhece, transfira seu saldo para a conta segura, chave {chave}, ou sua conta será bloqueada.",
    "Central {banco}: sua conta foi comprometida. Para proteger seu saldo, transfira imediatamente para a conta segura, chave {chave}. Não ignore.",
    "ATENÇÃO: seu CPF está com pendência no Serasa. Regularize hoje com desconto de 90% via Pix para {chave}. Valor: R$ {valor}.",
    "Boleto {loja} em atraso! Evite negativação pagando R$ {valor} via Pix na chave {chave} até as 18h.",
    "Seu pedido {pedido} da {loja} está retido na transportadora. Pague a taxa de liberação de R$ {valor} via Pix {chave} para receber hoje.",
    "PARABÉNS! Você foi sorteado no {loja} Premiado e ganhou R$ 5.000. Para liberar, pague a taxa de R$ {valor} no Pix {chave} em até 1 hora.",
    "Você ganhou um iPhone 16 na promoção {loja}! Confirme o frete de R$ {valor} pela chave Pix {chave} e receba em 24h.",
    "Oi, fiz um Pix pra você por engano de R$ {valor}. Pode devolver na chave {chave}? Preciso muito desse dinheiro, é do aluguel.",
    "Boa tarde, caiu um Pix de R$ {valor} na sua conta que era pra outra pessoa. Por favor estorne pra chave {chave} hoje ainda.",
    "Receita Federal: sua restituição de R$ {valor} está bloqueada. Regularize pagando a taxa de R$ 47,90 no Pix {chave}.",
    "Detran: multa de R$ {valor} vence hoje. Pague com 40% de desconto via Pix {chave} e evite a suspensão da CNH.",
    "{nome}, seu benefício do INSS foi suspenso. Reative agora pagando a taxa administrativa via Pix {chave}. Prazo: 2 horas.",
    "Oi {parente}, tô numa situação chata, bati o carro e preciso pagar o guincho agora. Manda R$ {valor} no Pix {chave}? Depois te explico.",
    "Aqui é do RH da {loja}. Sua vaga foi aprovada! Para emitir a carteira de trabalho digital, pague R$ {valor} no Pix {chave}.",
    "Seu WhatsApp será desativado em 24h por violação. Para manter, confirme seu cadastro pagando R$ {valor} via Pix {chave}.",
    "{banco} informa: sua fatura de R$ {valor} está vencida. Evite juros pagando agora via Pix na chave {chave}.",
    "Olá, sou o advogado do seu {parente}. Ele foi detido e precisa de R$ {valor} para a fiança agora. Pix na chave {chave}. Não ligue pra ele.",
    "Vaga de renda extra: ganhe R$ 300 por dia avaliando produtos. Taxa de cadastro única de R$ {valor} via Pix {chave}.",
    "Seu carro foi sorteado com IPVA grátis! Confirme pagando a taxa de R$ {valor} no Pix {chave} em até 30 minutos.",
    "{nome}, aqui é da {loja}. Houve uma cobrança duplicada de R$ {valor}. Para o estorno, confirme seus dados e pague a taxa de R$ 9,90 no Pix {chave}.",
    "Oi amor, é o {nome}, tô com o celular da minha colega. Me faz um Pix de R$ {valor} na chave {chave}? Explico quando chegar.",
    "{banco}: token expirado. Para não perder acesso ao app, faça um Pix de validação de R$ 1,00 para {chave} nos próximos 10 minutos.",
    "Sua conta de luz está para corte HOJE. Pague R$ {valor} via Pix {chave} e evite a suspensão do fornecimento.",
    "Oi, é da clínica. A consulta do seu {parente} precisa de sinal de R$ {valor} até as 17h. Chave Pix: {chave}.",
    "Investimento garantido: 30% ao mês. Comece com R$ {valor} via Pix {chave}. Últimas 3 vagas, responde rápido!",
    "Correios: encomenda {pedido} aguardando pagamento de taxa alfandegária de R$ {valor}. Pix: {chave}. Prazo final: hoje.",
    "{parente}, mudei de número. Minha conta foi bloqueada e preciso pagar o cartão hoje. Faz um Pix de R$ {valor} pra {chave}? Te devolvo sexta.",
];

/// Mensagens legítimas com remetentes coerentes com o conteúdo.
const LEGITIMAS: &[(&str, &[&str])] = &[
    ("Oi {parente}! Cheguei bem, viagem tranquila. Depois te ligo pra contar.", &["Filha", "Lucas", "Júlia", "Pedro"]),
    ("{nome}, o churrasco de sábado vai ser na casa do Rafa. Leva o carvão? Eu levo a carne.", &["Marcos", "Bruno", "Rafael"]),
    ("Pedido {pedido} confirmado! {loja} agradece a compra. Previsão de entrega: 3 dias úteis.", &["{loja}", "SMS {loja}"]),
    ("Oi, é a Ana do dentista. Confirmando sua consulta amanhã às 14h. Pode responder SIM?", &["Ana (dentista)", "Clínica Sorriso"]),
    ("Lembrete: a mensalidade da academia vence dia 10. Se preferir Pix, a chave é {chave}.", &["Academia FitMais"]),
    ("Oi filho, comprei o presente da vovó. Foi R$ {valor}, dividimos depois, sem pressa.", &["Mãe", "Pai"]),
    ("Boa tarde! Seu carro está pronto. Ficou R$ {valor} a revisão. Pode pagar quando buscar, aceitamos Pix ({chave}) ou cartão.", &["Oficina do Beto"]),
    ("{loja}: seu pedido {pedido} saiu para entrega. Acompanhe pelo app.", &["{loja}", "SMS {loja}"]),
    ("Amiga, a rifa da escola é R$ {valor} o número. Se quiser, o Pix é {chave}, mas pode pagar na terça também.", &["Carla", "Fernanda", "Beatriz"]),
    ("Oi {nome}, tudo bem? Manda o endereço novo que quero te mandar um convite.", &["Tia Lúcia", "Prima Bia", "Rafael"]),
    ("Nota fiscal do seu pedido {pedido} disponível na sua conta {loja}.", &["{loja}"]),
    ("Pai, cheguei na faculdade. A prova foi tranquila. Almoço aí domingo?", &["Filha", "Filho"]),
    ("Oi, aqui é o Marcos do apartamento 302. Reunião de condomínio quinta às 19h no salão.", &["Marcos 302", "Síndico"]),
    ("Sua fatura {banco} de R$ {valor} fecha dia 25. Consulte no app.", &["{banco}"]),
    ("Lembrete: consulta com Dr. Paulo amanhã 9h. Traga os exames.", &["Clínica Dr. Paulo", "Recepção Dr. Paulo"]),
    ("{nome}, obrigado pelo Pix! Já recebi os R$ {valor} do rateio da pizza.", &["Bruno", "Lucas", "Marcos"]),
    ("Oi vó, feliz aniversário! Vou passar aí à tarde com as crianças.", &["Filha", "Neta Júlia"]),
    ("{loja}: seu carrinho ficou salvo. Os itens continuam disponíveis por 7 dias.", &["{loja}"]),
    ("Tio, o jogo é às 16h. A gente se encontra no portão B?", &["Sobrinho Pedro", "Rafael"]),
    ("Bom dia! A diarista vem quarta. Deixei R$ {valor} em cima da mesa, se faltar me avisa.", &["Mãe", "Esposa", "Marido"]),
];

const PARENTES: &[&str] = &["mãe", "pai", "tia", "vó", "irmão", "filha", "tio", "prima"];
const NOMES: &[&str] = &["Lucas", "Ana", "Pedro", "Júlia", "Marcos", "Carla", "Bruno", "Fernanda", "Rafael", "Beatriz"];
const BANCOS: &[&str] = &["Banco do Brasil", "Itaú", "Bradesco", "Caixa", "Nubank", "Santander"];
const LOJAS: &[&str] = &["Magazine Luiza", "Mercado Livre", "Shopee", "Amazon", "Casas Bahia", "Americanas"];

fn preencher(rng: &mut ChaCha8Rng, tpl: &str, chave: &str, valor_centavos: u32) -> String {
    let valor = format!("{},{:02}", valor_centavos / 100, valor_centavos % 100);
    let pedido = format!("#{}", rng.gen_range(100_000..999_999));
    tpl.replace("{parente}", PARENTES.choose(rng).unwrap())
        .replace("{nome}", NOMES.choose(rng).unwrap())
        .replace("{banco}", BANCOS.choose(rng).unwrap())
        .replace("{loja}", LOJAS.choose(rng).unwrap())
        .replace("{pedido}", &pedido)
        .replace("{valor}", &valor)
        .replace("{chave}", chave)
}

fn telefone(rng: &mut ChaCha8Rng) -> String {
    let ddd = [11, 21, 31, 41, 51, 61, 71, 81, 85, 92].choose(rng).unwrap();
    format!("+55 {} 9{:04}-{:04}", ddd, rng.gen_range(1000..9999), rng.gen_range(0..9999))
}

fn nova_chave(rng: &mut ChaCha8Rng, usadas: &mut HashSet<String>) -> String {
    loop {
        let k = match rng.gen_range(0..3) {
            0 => format!("{}9{:08}", [11, 21, 31, 41, 51, 61, 71, 81].choose(rng).unwrap(), rng.gen_range(0..99_999_999u32)),
            1 => format!("{}{}@gmail.com", NOMES.choose(rng).unwrap().to_lowercase(), rng.gen_range(10..9999)),
            _ => format!("{:08x}-{:04x}", rng.gen::<u32>(), rng.gen::<u16>()),
        };
        if usadas.insert(k.clone()) {
            return k;
        }
    }
}

fn ts_comercial(rng: &mut ChaCha8Rng, dia: u32) -> u32 {
    let hora = loop {
        let h = rng.gen_range(0..24u32);
        let peso = if (8..=22).contains(&h) { 3 } else { 1 };
        if rng.gen_range(0..3) < peso {
            break h;
        }
    };
    dia * 86_400 + hora * 3_600 + rng.gen_range(0..3_600)
}

fn main() -> Result<()> {
    let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("data");
    std::fs::create_dir_all(&dir)?;
    let mut rng = ChaCha8Rng::seed_from_u64(42);
    let mut txs: Vec<Tx> = Vec::with_capacity(N_TX_NORMAIS + 1_000_000);

    // Pesos dos hubs (alguns muito grandes).
    let pesos: Vec<f64> = (0..N_HUBS).map(|i| 1.0 / ((i + 1) as f64).powf(0.8)).collect();
    let soma_pesos: f64 = pesos.iter().sum();
    let escolher_hub = |rng: &mut ChaCha8Rng| -> u32 {
        let mut r = rng.gen::<f64>() * soma_pesos;
        for (i, p) in pesos.iter().enumerate() {
            r -= p;
            if r <= 0.0 {
                return i as u32;
            }
        }
        N_HUBS - 1
    };
    let normal = |rng: &mut ChaCha8Rng| -> u32 { rng.gen_range(N_HUBS..N_CONTAS) };
    let ln_pequeno = LogNormal::new((8_000f64).ln(), 1.1).unwrap();
    let ln_lote = LogNormal::new((30_000f64).ln(), 0.8).unwrap();

    // Transações normais.
    for _ in 0..N_TX_NORMAIS {
        let origem = normal(&mut rng);
        let destino = if rng.gen::<f64>() < 0.5 {
            escolher_hub(&mut rng)
        } else {
            loop {
                let d = normal(&mut rng);
                if d != origem {
                    break d;
                }
            }
        };
        let valor = ln_pequeno.sample(&mut rng).clamp(500.0, 500_000.0) as u32;
        let dia = rng.gen_range(0..DIAS);
        txs.push(Tx { origem, destino, valor, ts: ts_comercial(&mut rng, dia) });
    }

    // Lotes diários dos hubs (fornecedores, salários).
    for h in 0..N_HUBS {
        let diario = 10 + (pesos[h as usize] / pesos[0] * 1500.0) as u32;
        for dia in 0..DIAS {
            let base = dia * 86_400 + 9 * 3_600 + rng.gen_range(0..7_200);
            for _ in 0..diario {
                let valor = ln_lote.sample(&mut rng).clamp(2_000.0, 2_000_000.0) as u32;
                txs.push(Tx { origem: h, destino: normal(&mut rng), valor, ts: base + rng.gen_range(0..1_800) });
            }
        }
    }

    // Quadrilhas.
    let mut reservadas: HashSet<u32> = HashSet::new();
    let mut chaves_usadas: HashSet<String> = HashSet::new();
    let mut chaves: HashMap<String, u32> = HashMap::new();
    let mut quadrilhas: Vec<Quadrilha> = Vec::new();
    let reservar = |rng: &mut ChaCha8Rng, reservadas: &mut HashSet<u32>| -> u32 {
        loop {
            let c = rng.gen_range(N_HUBS..N_CONTAS);
            if reservadas.insert(c) {
                return c;
            }
        }
    };
    for _ in 0..N_QUADRILHAS {
        let no = reservar(&mut rng, &mut reservadas);
        let n_lar = rng.gen_range(12..=18);
        let laranjas: Vec<u32> = (0..n_lar).map(|_| reservar(&mut rng, &mut reservadas)).collect();
        let saque: Vec<u32> = (0..2).map(|_| reservar(&mut rng, &mut reservadas)).collect();
        let dia = rng.gen_range(1..DIAS - 1);
        let inicio_ts = dia * 86_400 + rng.gen_range(9..20) * 3_600 + rng.gen_range(0..3_600);
        let n_vitimas = rng.gen_range(20..=40);
        let mut total: u64 = 0;
        for _ in 0..n_vitimas {
            let v = loop {
                let c = normal(&mut rng);
                if !reservadas.contains(&c) {
                    break c;
                }
            };
            let valor = rng.gen_range(30_000..300_000u32);
            total += valor as u64;
            txs.push(Tx { origem: v, destino: no, valor, ts: inicio_ts + rng.gen_range(0..7_200) });
        }
        let t_repasse = inicio_ts + 7_200 + rng.gen_range(60..900);
        let por_laranja = (total / n_lar as u64) as u32;
        for &l in &laranjas {
            let valor = por_laranja - rng.gen_range(0..por_laranja / 50);
            txs.push(Tx { origem: no, destino: l, valor, ts: t_repasse + rng.gen_range(0..300) });
            let destino = *saque.choose(&mut rng).unwrap();
            let taxa = rng.gen_range(0..valor / 100);
            txs.push(Tx { origem: l, destino, valor: valor - taxa, ts: t_repasse + 300 + rng.gen_range(300..2_400) });
        }
        let chave = nova_chave(&mut rng, &mut chaves_usadas);
        chaves.insert(chave.clone(), no);
        quadrilhas.push(Quadrilha { chave, no, laranjas, saque, inicio_ts });
    }

    txs.sort_by_key(|t| t.ts);

    // Mensagens.
    let mut msgs: Vec<(u32, String, String, String, bool)> = Vec::new();
    for i in 0..N_MSG_GOLPE {
        let q = &quadrilhas[i % N_QUADRILHAS];
        let tpl = GOLPES[i % GOLPES.len()];
        let valor = rng.gen_range(8_000..250_000u32);
        let texto = preencher(&mut rng, tpl, &q.chave, valor);
        let remetente = match rng.gen_range(0..3) {
            0 => telefone(&mut rng),
            1 => format!("SMS {}", rng.gen_range(20_000..29_999)),
            _ => format!("{} (número desconhecido)", telefone(&mut rng)),
        };
        let ts = q.inicio_ts - rng.gen_range(120..600);
        msgs.push((ts, remetente, texto, q.chave.clone(), true));
    }
    for i in 0..N_MSG_LEGIT {
        let (tpl, remetentes) = LEGITIMAS[i % LEGITIMAS.len()];
        let chave = nova_chave(&mut rng, &mut chaves_usadas);
        let conta = if tpl.contains("{loja}") { escolher_hub(&mut rng) } else { normal(&mut rng) };
        chaves.insert(chave.clone(), conta);
        let valor = rng.gen_range(1_500..90_000u32);
        // Mesma loja/banco no texto e no remetente.
        let loja = *LOJAS.choose(&mut rng).unwrap();
        let banco = *BANCOS.choose(&mut rng).unwrap();
        let texto = preencher(&mut rng, &tpl.replace("{loja}", loja).replace("{banco}", banco), &chave, valor);
        let remetente = remetentes.choose(&mut rng).unwrap().replace("{loja}", loja).replace("{banco}", banco);
        let dia = rng.gen_range(1..DIAS - 1);
        msgs.push((ts_comercial(&mut rng, dia), remetente, texto, chave, false));
    }
    msgs.shuffle(&mut rng);
    let mensagens: Vec<Mensagem> = msgs
        .into_iter()
        .enumerate()
        .map(|(i, (ts, remetente, texto, chave, golpe_real))| Mensagem { id: i as u32, ts, remetente, texto, chave, golpe_real })
        .collect();

    let meta = Meta { n_contas: N_CONTAS, n_transacoes: txs.len() as u32, hubs: (0..N_HUBS).collect(), quadrilhas };
    data::write_transacoes(&dir, N_CONTAS, &txs)?;
    data::write_chaves(&dir, &chaves)?;
    data::write_meta(&dir, &meta)?;
    data::write_mensagens(&dir, &mensagens)?;
    println!(
        "gerado em {}: {} contas, {} transações, {} quadrilhas, {} mensagens",
        dir.display(),
        N_CONTAS,
        txs.len(),
        meta.quadrilhas.len(),
        mensagens.len()
    );
    Ok(())
}
