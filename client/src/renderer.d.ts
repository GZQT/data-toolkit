import { ProgressInfo, UpdateCheckResult } from 'electron-updater'
import { FileFilter } from 'electron'
import { Report } from 'pages/report/report-store'

export interface WindowsApi {
  minimize: () => void
  toggleMaximize: () => void
  close: () => void
}

export interface FileApi {
  getFileCount: (file: string) => Promise<{ total: number, updatedDate?: Date }>
  selectFiles: (multiSelections?: boolean, openDirectory?: boolean, filters?: FileFilter[]) => Promise<string[] | undefined>
  openFileDirectory: (file: string) => void
  openApplicationDirectory: (dirname: string) => void
  openExeDirectory: () => void
  getApplicationDirectoryFiles: (dirname: string) => string[]
  getCsvHeader: (file: string) => Promise<string[]>
  openExternalLink: (url: string) => void
  checkExistPath: (file: string) => boolean
  openDirectory: (path: string) => void
}

export interface ApplicationApi {
  checkUpdate: () => Promise<UpdateCheckResult | null>
  downloadUpdate: () => void
  installUpdateApp: () => void
  onUpdateProgress: (func: (info: ProgressInfo) => void) => void
  getRemoteServer: () => Promise<string>
  setRemoteServer: (address: string) => void
}

export interface KernelApi {
  start: () => Promise<boolean | string>
  restartKernel: () => Promise<boolean | string>
  getKernelPort: () => Promise<number>
  getKernelAvailablePort: () => Promise<number>
}

export interface ReportApi {
  generate: (report: Report) => Promise<void>
}

declare global {
  interface Window {
    WindowsApi: WindowsApi
    FileApi: FileApi
    KernelApi: KernelApi
    ApplicationApi: ApplicationApi
    ReportApi: ReportApi
  }
}
