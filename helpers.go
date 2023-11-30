package main

import (
	"fmt"
	"github.com/tcolgate/mp3"
	"image"
	_ "image/jpeg"
	_ "image/png"
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
				fmt.Println(absolutePath)

				log.Fatal("Error copying file:", e)
			}
		}
	}
}
func unwrapEmbeddedDefaultCharacter() {
	logM(1, "Unpacking Default Files (Concurrent)...")

	defaultsPath := filepath.Join(generateDir, "defaults")
	defaultsPathExists, _ := pathExists(defaultsPath)
	if defaultsPathExists {
		os.Remove(defaultsPath)
	}

	dir, err := defaults.ReadDir("defaults")
	if err != nil {
		log.Fatal(err)
	}
	unwrapHelper(generateDir, "defaults", dir)
}

func copyMap(m map[string]string) map[string]string {
	m2 := make(map[string]string, len(m))
	for id := range m {
		m2[id] = m[id]
	}
	return m2
}

func openImage(filePath string) image.Image {
	f, err := os.Open(filePath)
	if err != nil {
		fmt.Println("Error opening image at ", filePath)
		log.Fatal(err)
	}
	defer f.Close()
	image, _, err := image.Decode(f)
	if err != nil {
		fmt.Println("Error decoding image at ", filePath)
		log.Fatal(err)
	}
	return image
}

func getAudioFileDuration(filePath string) float64 {
	file, err := os.Open(filePath)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	switch getFileFormat(filePath) {
	case "mp3":
		t := 0.0
		d := mp3.NewDecoder(file)
		var f mp3.Frame
		skipped := 0
		for {
			if err := d.Decode(&f, &skipped); err != nil {
				if err == io.EOF {
					break
				}
				log.Fatal(err)
			}
			t = t + f.Duration().Seconds()
		}
		return t
	default:
		log.Fatal("unsupported audio file format, please use an mp3")
	}

	return -1
}

// helper function to extract the file format from file path
func getFileFormat(filePath string) string {
	fileExtension := filePath[len(filePath)-3:]
	if fileExtension == "wav" {
		return "wav"
	} else if fileExtension == "mp3" {
		return "mp3"
	}
	return ""
}
