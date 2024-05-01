export interface WindowsApi {
  minimize: () => void
  toggleMaximize: () => void
  close: () => void
}

export interface FileApi {
  getFileCount: () => Promise<number>
  selectFiles: (multiSelections: boolean) => Promise<string[] | undefined>
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
