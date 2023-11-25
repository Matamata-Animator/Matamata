package main

import (
	"fmt"
	"os"
)

func pathExists(path string) (bool, error) {
	_, err := os.Stat(path)
	if err == nil {
		return true, nil
	}
	if os.IsNotExist(err) {
		return false, nil
	}
	return false, err
}
func main() {
	modelDownloaded, _ := pathExists("model/")
	if !modelDownloaded {
		fmt.Println("Downloading Vosk Modek, this only needs to happen the first time you run the program")
		getModel()
	}
	fmt.Println("Done!")
}
