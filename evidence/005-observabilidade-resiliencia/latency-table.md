| stage | event | status | duration_ms |
|---|---|---|---:|
| request | complete | ok | 30.41 |
| classify_msg | complete | ok | 0.34 |
| gather_needs | complete | ok | 0.16 |
| prepare_catalog | complete | ok | 0.06 |
| catalog.notebook | complete | ok | 5.76 |
| catalog.desktop | complete | ok | 5.73 |
| tool.buscar_produtos | complete | ok | 10.00 |
| catalog.consolidate | complete | ok | 0.00 |
| catalog.compare | complete | skipped | 0.00 |
| compare_catalog_products | complete | ok | 2.94 |
| tool.comparar_produtos | complete | ok | 2.28 |
| recommend | complete | ok | 0.18 |
| report | complete | ok | 0.71 |
| tool.gerar_relatorio | complete | ok | 0.08 |
| respond | complete | ok | 0.20 |

A captura normal foi executada via `POST /agent/send/`, com catálogo HTTP local `catalog:8080/products`. Logs e métricas compartilham os mesmos IDs técnicos. Sem anomalia acima de 500 ms; etapa mais lenta: `request` (30,41 ms).

A captura de falha usa `catalog:8080/products/error`. O cliente aplicou retry limitado e o fluxo continuou com fallback local. A investigação correspondente está em `failure-runtime-analysis.json`.
