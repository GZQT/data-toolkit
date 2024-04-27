export interface WindowsApi {
  minimize: () => void
  toggleMaximize: () => void
  close: () => void
}

export interface FileApi {
  getFileCount: () => Promise<number>
}

declare global {
  interface Window {
    WindowsApi: WindowsApi
    FileApi: FileApi
  }
}
