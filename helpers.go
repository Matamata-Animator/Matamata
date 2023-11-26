package main

import "fmt"

var loglevel int8 = 1

func logM(level int8, message ...any) {
	if loglevel >= level {
		fmt.Println(message...)
	}
	fmt.Println()
}

func filter[T any](ss []T, test func(T) bool) (ret []T) {
	for _, s := range ss {
		if test(s) {
			ret = append(ret, s)
		}
	}
	return
}
