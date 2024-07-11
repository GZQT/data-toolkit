export const handleOpenFile = (file: string) => {
  if (isElectron()) {
    window.FileApi.openFileDirectory(file)
  }
}

export const handleOpenDir = (path: string) => {
  if (isElectron()) {
    window.FileApi.openDirectory(path)
  }
}

export const handleHomeDirectoryOpenFile = (file: string) => {
  if (isElectron()) {
    window.FileApi.openApplicationDirectory(file)
  }
}

export const handleBrowser = (url: string) => {
  if (isElectron()) {
    window.FileApi.openExternalLink(url)
  }
}

export const handleExitApp = () => {
  if (isElectron()) {
    window.WindowsApi.close()
  }
}

export const handleOpenHome = () => {
  if (isElectron()) {
    window.FileApi.openApplicationDirectory('')
  }
}

export const handleOpenExe = () => {
  if (isElectron()) {
    window.FileApi.openExeDirectory()
  }
}

export const isElectron = (): boolean => process.env.MODE === 'electron'
