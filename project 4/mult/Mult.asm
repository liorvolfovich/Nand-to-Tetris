// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// Multiplies R0 and R1 and stores the result in R2.
//
// Assumptions:
// - R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.
// - You can assume that you will only receive arguments that satisfy:
//   R0 >= 0, R1 >= 0, and R0*R1 < 32768.
// - Your program does not need to test these conditions.
//
// Requirements:
// - Your program should not change the values stored in R0 and R1.
// - You can implement any multiplication algorithm you want.

// Put your code here.

//i=0
@i
M=0
//R2=0
@R2
M=0
//add R0 to R2, R1 times.
(LOOP)
    //if i=R1 goto END
    @i
    D=M
    @R1
    D=D-M
    @END
    D;JEQ
    //R2=R2+R0
    @R0
    D=M
    @R2
    M=M+D
    //i=i+1
    @i
    M=M+1
    //goto LOOP
    @LOOP
    0;JMP
(END)
    @END
    0;JMP



// //finding MAX(RO,R1)
// //if RO>R1 goto LARGER
// @R0
// D=M
// @R1
// D=D-M
// @LARGER
// D;JGT
// //a=R1, b=R0
// @R1
// D=M
// @a
// M=D
// @R0
// D=M
// @b
// M=D
// //goto START
// @START
// 0;JMP
// //a=R0, b=R1
// (LARGER)
//     @R0
//     D=M
//     @a
//     M=D
//     @R1
//     D=M
//     @b
//     M=D
// (START)
//     //i=0
//     @i
//     M=0
//     //R2=0
//     @R2
//     M=0
// //add a to R2, b times.
// (LOOP)
//     //if i=b goto END
//     @i
//     D=M
//     @b
//     D=D-M
//     @END
//     D;JEQ
//     //R2=R2+a
//     @a
//     D=M
//     @R2
//     M=M+D
//     //i=i+1
//     @i
//     M=M+1
//     //goto LOOP
//     @LOOP
//     0;JMP
// (END)
//     @END
//     0;JMP
