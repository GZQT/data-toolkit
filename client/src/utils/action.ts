export const handleOpenFile = (file: string) => {
  window.FileApi.openFileDirectory(file)
}

export const handleHomeDirectoryOpenFile = (file: string) => {
  window.FileApi.openApplicationDirectory(file)
}

export const handleBrowser = (url: string) => {
  window.FileApi.openExternalLink(url)
}

export const isElectron = (): boolean => process.env.MODE === 'electron'
