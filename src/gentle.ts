// const axios = require("axios").default;
import fs from "fs";

// // import { curly, Curl } from "node-libcurl";
// import axios from "axios";
// import FormData from "form-data";

let url = "http://localhost:8765/transcriptions?async=false";

export async function gentleAlign(audio_path: string, script_path: string) {
  //   const form = new FormData();
  //   form.append("audio", fs.createReadStream(audio_path));
  //   form.append("transcript", fs.createReadStream(script_path));
  //   axios.post(url, form, { headers: form.getHeaders() });
}
