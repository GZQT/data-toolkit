export interface PageContent<T> {
  items: T[],
  total: number | null;
  page: number | null;
  size: number | null;
  pages?: number | null;
}
