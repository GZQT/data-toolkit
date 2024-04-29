export interface WindowsApi {
  minimize: () => void
  toggleMaximize: () => void
  close: () => void
}

export interface FileApi {
  getFileCount: () => Promise<number>
}

export interface KernelApi {
  start: () => Promise<boolean | string>
}

declare global {
  interface Window {
    WindowsApi: WindowsApi
    FileApi: FileApi,
    KernelApi: KernelApi
  }
}
