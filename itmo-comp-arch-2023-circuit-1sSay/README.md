# [![Ci/CD](../../actions/workflows/ci.yaml/badge.svg?branch=main&event=workflow_dispatch)](../../actions/workflows/ci.yaml)

## Проверка verilog локально (из корня репозитория):

1. `iverilog -g2012 -o stack_tb.out stack_behaviour_tb.sv`
2. `vvp stack_tb.out +TIMES=3 +OUTCSV=st_stack_3.csv`
3. `python st_stack_3.csv .github/workflows/ref_stack_3.csv`

Также посмотреть логи можно в файле `st_stack_3.csv`. Проверяем значения на выходе только при CLK=1.

> Примечание: вместо `edge signal` используйте `signal`

## Проверка logisim локально (из корня репозитория):

WIP
