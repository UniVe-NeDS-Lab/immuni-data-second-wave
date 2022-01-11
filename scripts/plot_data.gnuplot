system "mkdir -p ../images/"

set term eps enhanced size 4,3
set output '../images/immuni-ppv.eps'
set datafile separator ','
set key autotitle columnhead
set xdata time
set timefmt "%Y-%m-%d"
set ytics nomirror
set title "γ(t)"
set key off
set logscale y
set xtics rotate by 30 right

set style rect fc lt -1 fs solid 0.15 noborder
set obj rect from "2020-8-13", graph 0 to "2020-11-03", graph 1

const(x) = 0.0085
const2(x) = 0.006
set style line 1 linetype 5 linecolor 0 dt "-"
set style line 2 linetype 1 linecolor 0
set ytics (0.001, 0.01, 0.002, 0.003, 0.006, 0.0085, 0.1) nomirror
set for [i=0:10] ytics add (0.001*i 1)
set for [i=0:10] ytics add (0.01*i 1)
set for [i=0:10] ytics add (0.1*i 1)
set ytics scale 1,1
set xlabel "time"
set yrange [0.002: 0.1]
plot const(x) w l ls 1, const2(x) w l ls 1, '../data/italian-data.csv' i 0 u "data":"PPV-2.8"  w lp pt 13 ps 0.5 dt "-" lc rgb "black"

reset
set term eps enhanced size 4,3
set output '../images/immuni-gamma-zoom.eps'
set datafile separator ','
set key autotitle columnhead
set xdata time
set timefmt "%Y-%m-%d"
set ytics nomirror
set title "γ(t)"
set key off
set logscale y
set xtics rotate by 30 right

set xrange ["2020-8-13":"2020-11-04"]

nationalavg = 0.00679
nationalavg2 = 0.00058
set style line 1 linetype 5 linecolor 0 dt "-"
set style line 2 linetype 1 linecolor 0
set ytics (0.001, 0.002, 0.003, 0.006, 0.0085) nomirror
set for [i=0:10] ytics add (0.001*i 1)
set for [i=0:10] ytics add (0.01*i 1)
set for [i=0:10] ytics add (0.1*i 1)
set ytics scale 1,1
set xlabel "time"
set style fill transparent solid 0.5 


plot nationalavg w l ls 1,\
'../data/regions.csv' using "date":"min":"max" with filledcurves lc "skyblue",\
'../data/italian-data.csv' using "data":"PPV-1.7":"PPV-2.8" with filledcurves lc "green",\
'../data/regions.csv' i 0 u "date":"rescaled"  w l lc rgb "black" lw 5 dt "-"

reset
set term eps enhanced size 4,3
set output '../images/immuni-rho.eps'
set datafile separator ','
set key autotitle columnhead
set xdata time
set timefmt "%Y-%m-%d"
set ytics nomirror
set title "{/Symbol r}(t)"
set key top center
set logscale y
set xtics rotate by 30 right
set style rect fc lt -1 fs solid 0.15 noborder
set obj rect from "2020-8-13", graph 0 to "2020-11-03", graph 1
const(x) = 3.5
const2(x) = 105
set ytics (1,3.5,10,105,1000)
set for [i=0:10] ytics add (0.1*i 1)
set for [i=0:10] ytics add (i 1)
set for [i=0:10] ytics add (10*i 1)
set xlabel "time"
set style line 1 linetype 5 linecolor 0 dt "-"
plot '../data/italian-data.csv' i 0 u "data":"rho" w lp t "{/Symbol r}(t)" pt 7 ps 0.5, 3.5 w l ls 1, 105 w l ls 1


reset
set term eps enhanced size 4,3
set datafile separator ','
set key autotitle columnhead
set xdata time
set timefmt "%Y-%m-%d"
set xtics rotate by 30 right
set title "Daily number of new Infected People and R_t"
set logscale y
unset logscale y2
set y2range [0:2]
set y2tics (0,0.5,1,1.5,2)
set ytics nomirror
set style rect fc lt -1 fs solid 0.15 noborder
set obj rect from "2020-8-13", graph 0 to "2020-11-03", graph 1
set output '../images/italian-infected.eps'
set xlabel "time"
set key at graph 0.72, graph 1
plot '../data/italian-data.csv' i 0 u "data":"nuovi_positivi" w lp pt 7 ps 0.4 t 'Daily Positives', ''  u "data":"Rt" axis x1y2 w l t 'R_t'

reset
set term eps enhanced size 4,3
set datafile separator ','
set key autotitle columnhead
set xdata time
set timefmt "%Y-%m-%d"
set xtics rotate by 30 right
set title "Daily Positives and App Downloads"
set logscale y
set y2tics #(0,0.5,1,1.5,2)
set ytics nomirror
set style rect fc lt -1 fs solid 0.15 noborder
set obj rect from "2020-8-13", graph 0 to "2020-11-03", graph 1
set obj rect from "2020-8-13", graph 0 to "2020-11-03", graph 1
set output '../images/downloads.eps'
set key at graph 0.72, graph 1
set xlabel "time"
plot '../data/italian-data.csv'  i 0 u "data":"nuovi_positivi" w lp pt 7 ps 0.4 t 'Daily Positives', '../data/italian-data.csv'  u "data":"ios_android_total" axis x1y2 w lp pt 13 ps 0.5 t 'Downloads'


reset
set term eps enhanced #size 5,3
set datafile separator ','
set key autotitle columnhead
set xdata time
set timefmt "%Y-%m-%d"
set xtics rotate by 30 right
set size ratio 0.5
set style rect fc lt -1 fs solid 0.15 noborder
set obj rect from "2020-8-13", graph 0 to "2020-11-03", graph 1
set title "Required Daily Tests Per Adult"
set output '../images/italian-tpp.eps'
set xlabel "time"
plot '../data/italian-data.csv' i 0 u "data":"daily_tests_per_person" w lp pt 7 ps 0.4 t ''

reset
set term eps enhanced #size 5,3
set datafile separator ','
set key autotitle columnhead
set xdata time
set timefmt "%Y-%m-%d"
set xtics rotate by 30 right
set size ratio 0.5
set style rect fc lt -1 fs solid 0.15 noborder
set obj rect from "2020-8-13", graph 0 to "2020-11-03", graph 1
set title 'α(t)'
set output '../images/italian-alpha.eps'
set xlabel "time"
set style line 1 linetype 5 linecolor 0 dt "-"
plot '../data/italian-data.csv' i 0 u "data":"alpha_weekly" w lp pt 7 ps 0.4 t '', 52.1 w l ls 1

