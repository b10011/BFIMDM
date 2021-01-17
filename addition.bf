Layer stepper   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   8
Layer input0    0   0   0   0   0   0   0   0   0   0   0   0   1   1   1   1   1
Layer input1    0   0   0   0   0   0   0   0   0   1   0   1   0   1   1   1   0
Layer sum
Layer tmp0
Layer tmp1
Layer tmp2
Layer tmp3

>>>>>>>>>>>>>>>>

#init

double the bit value
[-<+<+>>]<[->+<]<[->>+<<]>>

spread the value to left
[[-<+>]<->+<]

go to stepper's rightmost cell containing value 1
>[>]<

copy input0 layer to sum layer using tmp0 layer
[$[-$$+$+^^^]^<]>[>]<[$$$$[-^^^+$$$]^^^^<]>[>]<

copy input1 layer to sum layer using tmp0 layer
[$$[-$+$+^^]^^<]>[>]<[$$$$[-^^+$$]^^^^<]>[>]<

SPREAD BITS
[
    add the continuation flag below the digit
    $$$$+

    [
        clear the continuation flag
        [-]

        copy cell at sum layer to tmp0 and tmp1 using tmp2
        ^[-$+$+$+^^^]$$$[-^^^+$$$]^^^

        if tmp0 is not zero add one to flags at tmp2 and tmp3
        $[[-]$$+$+^^^]

        if tmp1 is not one add one to flags at tmp2 and tmp3
        $-[[-]$+$+^^]

        subtract 1 from flags
        $-$-

        if tmp3 is not zero subtract 2 from sum and add 1 to the digit on left at sum
        [[-]^^^^--<+>$$$$]

        move continuation flag from tmp2 to tmp0
        ^[-^^+$$]

        go to tmp0
        ^^
    ]

    move to next stepper at left
    ^^^^<
]

UNSPREAD STEPPER
>>[[<->+>]<[<]>>]<[--<+>]<[->+<]>

#result
