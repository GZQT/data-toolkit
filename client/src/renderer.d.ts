import { ProgressInfo, UpdateCheckResult } from 'electron-updater'

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
  openExeDirectory: () => void
  getApplicationDirectoryFiles: (dirname: string) => string[]
  getCsvHeader: (file: string) => Promise<string[]>
  openExternalLink: (url: string) => void
}

export interface ApplicationApi {
  checkUpdate: () => Promise<UpdateCheckResult | null>
  downloadUpdate: () => void
  installUpdateApp: () => void
  onUpdateProgress: (func: (info: ProgressInfo) => void) => void
}

export interface KernelApi {
  start: () => Promise<boolean | string>
  restartKernel: () => Promise<boolean | string>
  getKernelPort: () => Promise<number>
  getKernelAvailablePort: () => Promise<number>
}

declare global {
  interface Window {
    WindowsApi: WindowsApi
    FileApi: FileApi,
    KernelApi: KernelApi,
    ApplicationApi: ApplicationApi
  }
}
