# CertifyAI

**Continuous compliance engine for AI runtimes.**

Test your LLM endpoints against prompt injection, jailbreaking, PII leakage, policy violation, hallucination, and bias — then generate audit-ready evidence mapped to EU AI Act, SOC 2 Type II, and NIST AI RMF.

## Delivery

Self-hosted boilerplate. No subscription. No cloud dependency. Bring your own LLM API key.

- **Free** (PyPI): CLI + TUI + 10 attack scenarios + JSON reports
- **Pro** ($149): + Web Dashboard + 30 attacks + PDF reports + compliance mappings + commercial license
- **Enterprise** ($499): + White-label + source access + priority updates + custom frameworks

## Status

**Pre-build** — Complete documentation suite (17 docs, 20K+ lines). Ready for implementation.

| Wave | Docs | Status |
|------|------|--------|
| Market Research + PRD + Architecture | 4 foundation docs | ✅ |
| UX + Tests + Attacks + Compliance + Security + DB | 6 product specs | ✅ |
| Pricing + GTM + Support + Licensing | 7 business docs | ✅ |

## Quick Start (when built)

```bash
pip install certifyai
certifyai init
certifyai run --provider openai --model gpt-4o
certifyai report --format pdf
certifyai vault --verify
```

## Documentation

See [`docs/`](./docs/) for the full specification suite — 17 documents covering market research, competitive analysis, PRD, technical architecture, UX flows, test strategy, attack catalog, compliance mapping, security architecture, database schema, pricing, GTM, support, and licensing.

## License

- Free tier: Apache 2.0
- Pro/Enterprise: Commercial license (see [`docs/commercial-license.md`](./docs/commercial-license.md))
