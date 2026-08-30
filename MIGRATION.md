# Migração do repositório legado para v2.1.0-rc1

Este documento registra a integração do Revenue Mechanics como componente principal sem apagar o histórico documental relevante do repositório.

## Substituir
- `README.md`
- `CHANGELOG.md`

## Preservar
- `LICENSE.txt` (conteúdo mantido)
- `CONTRIBUTING.md`
- `ROADMAP.md`

## Adicionar
- `revenue_mechanics.py`
- `reliability_registry.py`
- `docs/MATHEMATICAL_SPEC.md`
- `docs/VALIDATION_REPORT.md`
- `docs/PRODUCTION_GATES.md`
- `tests/test_revenue_mechanics.py`
- `scripts/validate_production.py`
- `AGENTS.md`
- `skills/revenue-mechanics/`
- `agent/`
- `examples/`
- `.github/workflows/production-gates.yml`
- `.gitignore`

## Validação local

```bash
python scripts/validate_production.py
```

Não promover um release final se o gate não retornar `PASS` após qualquer alteração futura. Durante o backtesting longitudinal, manter a série `2.1.0-rcN`.
