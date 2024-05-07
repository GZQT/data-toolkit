export interface WindowsApi {
  minimize: () => void
  toggleMaximize: () => void
  close: () => void
}

export interface FileApi {
  getFileCount: (file: string) => Promise<{ total: number, updatedDate?: Date }>
  selectFiles: (multiSelections: boolean) => Promise<string[] | undefined>
  openFileDirectory: (file: string) => void
  openApplicationDirectory: (dirname: string) => void
  countFiles: (dirname: string) => Promise<number>
  getCsvHeader: (file: string) => Promise<string[]>
  openExternalLink: (url: string) => void
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
