// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.

// if length <= 1 goto END
@R15
D=M
D=D-1
@END
D;JLE
(MAX)
    //max = R14 (max represents the adress of the cell with the maximum value)
    @R14
    D=M
    @max
    M=D
    //i=0
    @i
    M=0
(MAXLOOP)
    //i=i+1
    @i
    M=M+1
    //if i = length goto MIN
    D=M
    @R15
    D=D-M
    @MIN
    D;JEQ
    //A=R[14+i]=arr[i]
    @R14
    D=M
    @i
    A=D+M
    //D=arr[i] - max
    D=M
    @max
    A=M
    D=D-M
    // if arr[i] <= max goto MAXLOOP
    @MAXLOOP
    D;JLE
    // max = R14 + i
    @R14
    D=M
    @i
    D=D+M
    @max
    M=D
    //goto MAXLOOP
    @MAXLOOP
    0;JMP

(MIN)
    //min = R14 (min represents the adress of the cell with the minimum value)
    @R14
    D=M
    @min
    M=D
    //i=0
    @i
    M=0
(MINLOOP)
    //i=i+1
    @i
    M=M+1
    //if i = length goto SWAP
    D=M
    @R15
    D=D-M
    @SWAP
    D;JEQ
    //A=R[14+i]=arr[i]
    @R14
    D=M
    @i
    A=D+M
    //D=arr[i] - min
    D=M
    @min
    A=M
    D=D-M
    // if arr[i] >= min goto MINLOOP
    @MINLOOP
    D;JGE
    // min = R14 + i
    @R14
    D=M
    @i
    D=D+M
    @min
    M=D
    //goto MINLOOP
    @MINLOOP
    0;JMP
(SWAP)
    //saving maxval
    @max
    A=M
    D=M
    @maxval
    M=D
    //saving minval
    @min
    A=M
    D=M
    @minval
    M=D
    //max=minval
    @minval
    D=M
    @max
    A=M
    M=D
    //min=maxval
    @maxval
    D=M
    @min
    A=M
    M=D
(END)
    @END
    0;JMP
