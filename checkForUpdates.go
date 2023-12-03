package main

import (
	"encoding/json"
	"fmt"
	"golang.org/x/mod/semver"
	"io/ioutil"
	"net/http"
)

type Release struct {
	TagName    string `json:"tag_name"`
	Draft      bool   `json:"draft"`
	Prerelease bool   `json:"prerelease"`
	HtmlUrl    string `json:"html_url"`
}

func checkForUpdates() {
	currentSemVer := "v5.0.4"

	logM(1, "Checking for Updates...")
	endpointUrl := "https://api.github.com/repos/Matamata-Animator/Matamata/releases?per_page=1"

	client := &http.Client{}

	req, err := http.NewRequest("GET", endpointUrl, nil)
	if err != nil {
		fmt.Println("Errored when creating request object", err)
		fmt.Println("Continuing...")
		return
	}
	req.Header.Add("Accept", "application/json")
	resp, err := client.Do(req)

	if err != nil || resp.StatusCode != 200 {
		fmt.Println("Errored when checking for updates.")
		fmt.Println(err)
		fmt.Println("Continuing...")
		return
	}
	defer resp.Body.Close()
	resp_body, _ := ioutil.ReadAll(resp.Body)
	res_str := string(resp_body)
	res_str = res_str[1 : len(res_str)-1]

	release := Release{}
	err = json.Unmarshal([]byte(res_str), &release)
	if err != nil {
		fmt.Printf("Error while parsing data: %s", err)
		fmt.Println("Continuing...")
		return
	}

	if release.Draft || release.Prerelease {
		return
	}

	if semver.Compare(currentSemVer, release.TagName) < 0 {
		colorReset := "\033[0m"
		colorRed := "\033[31m"
		fmt.Println(string(colorRed)+"New version available! ("+currentSemVer+" -> "+release.TagName+") You can download it from", release.HtmlUrl, string(colorReset))
	}

}
