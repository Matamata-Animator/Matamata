package main

import (
	"fmt"
)

var loglevel int8 = 0

func logM(message any, level int8) {
	if loglevel >= level {
		fmt.Println(message)
	}
}

func main() {
	args := parseArgs()
	logM(args, 3)

	downloadModel()
	//
	//fmt.Println("Done!")
}
