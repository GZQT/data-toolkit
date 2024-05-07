export const handleOpenFile = (file: string) => {
  window.FileApi.openFileDirectory(file)
}

export const handleHomeDirectoryOpenFile = (file: string) => {
  window.FileApi.openApplicationDirectory(file)
}
