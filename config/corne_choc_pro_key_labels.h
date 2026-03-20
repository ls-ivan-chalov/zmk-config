/*                   40 KEY MATRIX / LAYOUT MAPPING
 *
 *  Keebart Corne Choc Pro BT — five_col_layout (40 positions)
 *  Positions 5, 6 (row 0) and 17, 18 (row 1) are occupied by nice!view displays.
 *
 *  ╭─────────────────────┬─────────────────────╮
 *  │  0   1   2   3   4  │  7   8   9  10  11  │
 *  │ 12  13  14  15  16  │ 19  20  21  22  23  │
 *  │ 24  25  26  27  28  │ 29  30  31  32  33  │
 *  ╰──────╮  34  35  36  │ 37  38  39  ╭───────╯
 *         ╰──────────────┴─────────────╯
 *
 *  ╭─────────────────────┬─────────────────────╮
 *  │ LT4 LT3 LT2 LT1 LT0│ RT0 RT1 RT2 RT3 RT4│
 *  │ LM4 LM3 LM2 LM1 LM0│ RM0 RM1 RM2 RM3 RM4│
 *  │ LB4 LB3 LB2 LB1 LB0│ RB0 RB1 RB2 RB3 RB4│
 *  ╰──────╮ LH2 LH1 LH0 │ RH0 RH1 RH2 ╭──────╯
 *         ╰──────────────┴──────────────╯
 */

#pragma once

#define LT0  4  // left-top row
#define LT1  3
#define LT2  2
#define LT3  1
#define LT4  0

#define RT0  7  // right-top row (skip display positions 5, 6)
#define RT1  8
#define RT2  9
#define RT3 10
#define RT4 11

#define LM0 16  // left-middle row
#define LM1 15
#define LM2 14
#define LM3 13
#define LM4 12

#define RM0 19  // right-middle row (skip display positions 17, 18)
#define RM1 20
#define RM2 21
#define RM3 22
#define RM4 23

#define LB0 28  // left-bottom row
#define LB1 27
#define LB2 26
#define LB3 25
#define LB4 24

#define RB0 29  // right-bottom row
#define RB1 30
#define RB2 31
#define RB3 32
#define RB4 33

#define LH0 36  // left thumb keys
#define LH1 35
#define LH2 34

#define RH0 37  // right thumb keys
#define RH1 38
#define RH2 39

#define NUMROW
#define KEYS_L LT0 LT1 LT2 LT3 LT4 LM0 LM1 LM2 LM3 LM4 LB0 LB1 LB2 LB3 LB4
#define KEYS_R RT0 RT1 RT2 RT3 RT4 RM0 RM1 RM2 RM3 RM4 RB0 RB1 RB2 RB3 RB4
#define THUMBS_L LH0 LH1 LH2
#define THUMBS_R RH0 RH1 RH2
#define THUMBS THUMBS_L THUMBS_R
