let { PythonShell } = require("python-shell");
var path = require("path");
const Swal = require("sweetalert2");
var q = require("q");
const { exec } = require("child_process");

exec("where python\n", (error, stdout, stderr) => {
  if (error) {
    console.error(`exec error: ${error}`);
    return;
  }
  stdout_string = stdout;
  if (stdout_string.includes("Could not find")) {
    Swal.fire("You need python to run this software.");
    window.close();
  } else {
    stdout_path = stdout.split("\n");
    pyexe_path = stdout_path[0];
    py_path = pyexe_path.substr(0, pyexe_path.lastIndexOf("\\")) + "\\";
    console.log(py_path);
  }
});

window.addEventListener("DOMContentLoaded", function () {
  var pdf_list = [];
  var promises = [];

  const fileSelector = document.getElementById("pdf-selector");
  var pdf = fileSelector.addEventListener("change", (event) => {
    const fileList = event.target.files;
    const fileLength = event.target.files.length;
    Swal.fire({
      icon: "info",
      title: "Renaming in progress",
      text:
        "You have imported a total of " +
        fileLength +
        " file(s).Please wait shortly.",
    });
    console.log(fileList);
    (function process_pdf() {
      try {
        for (let i = 0; i < fileLength; i++) {
          promise = new Promise((resolve) => {
            send_pdf(fileList[i].path, resolve);
          });
          promise.then((d) => {
            console.log(promise);
            pdf_list.push(d);
            console.log(pdf_list);
            promises.push(promise);
            check_promise_length();
          });
        }

        function check_promise_length() {
          if (promises.length == fileLength) {
            swal_fire();
          }
        }

        function swal_fire() {
          Promise.all(promises).then(() => {
            console.log(pdf_list);
            pdf_list_res = pdf_list.join("");
            Swal.fire({
              icon: "success",
              html: pdf_list_res,
            });
            pdf_list_res = [];
            pdf_list = [];
            promise = [];
            promises = [];
          });
        }
      } catch (e) {
        return "error caught";
      }
    })();
  });

  function send_pdf(pdfpath, resolve, py_path) {
    var options = {
      scriptPath: path.join(__dirname, "../app.asar.unpacked/"),
      args: [pdfpath],
      mode: "text",
      pythonOptions: ["-u"],
      pythonPath: py_path,
    };

    var pyshell = new PythonShell("Batch PDF Renamer GUI.py", options);

    pyshell.stdout.on("data", function (data) {
      console.log(data);
      data = data.replace(/\r?\n/g, " ");
      listen_for_close(data);
    });

    pyshell.end(function (err, code, signal) {
      if (err) throw err;
      console.log("The exit code was: " + code);
      console.log("The exit signal was: " + signal);
    });

    function listen_for_close(data) {
      pyshell.stdout.on("close", function () {
        resolve(data);
      });
    }
  }

  false;
});
