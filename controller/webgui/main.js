/* 
This application was designed to run in a desktop window
however new versions do not support this anymore 
*/

const electron = require('electron')
const { app, BrowserWindow } = require('electron')

function createWindow () {
  let win = new BrowserWindow({ width: 1280, height: 720 });
  win.loadFile('index.html');
}

app.on('ready', createWindow)