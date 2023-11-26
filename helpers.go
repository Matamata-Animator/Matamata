package main

import (
	"fmt"
	"io"
	"io/fs"
	"log"
	"os"
	"path/filepath"
)

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

func unwrapHelper(cachepath string, relpath string, entries []fs.DirEntry) {
	for _, e := range entries {
		embedPath := filepath.Join(relpath, e.Name())
		absolutePath := filepath.Join(cachepath, embedPath)
		if e.IsDir() {
			os.MkdirAll(absolutePath, 0777)
			newPath := filepath.Join(relpath, e.Name())
			childEntries, _ := defaults.ReadDir(newPath)
			unwrapHelper(cachepath, newPath, childEntries)
		} else {
			embeddedFile, _ := defaults.Open(embedPath)
			defer embeddedFile.Close()
			destinationFile, _ := os.Create(absolutePath)
			defer destinationFile.Close()
			_, e := io.Copy(destinationFile, embeddedFile)
			if e != nil {
				log.Fatal("Error copying file:", e)
			}
		}
	}
}
func unwrapEmbeddedDefaultCharacter() {
	logM(1, "Unwrapping Default Character...")

	cacheDir, _ := os.UserCacheDir()
	matamataCachePath := filepath.Join(cacheDir, "matamata/")
	matamataPathExists, _ := pathExists(matamataCachePath)
	if !matamataPathExists {
		os.Mkdir(matamataCachePath, 0777)
	}
	defaultsPath := filepath.Join(matamataCachePath, "defaults")
	defaultsPathExists, _ := pathExists(defaultsPath)
	if defaultsPathExists {
		os.Remove(defaultsPath)
	}

	dir, err := defaults.ReadDir("defaults")
	if err != nil {
		log.Fatal(err)
	}
	unwrapHelper(matamataCachePath, "defaults", dir)
}
