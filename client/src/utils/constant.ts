export const GENERATOR_FILE_SPLIT = '_:_'

export const IMAGE_SUFFIX = ['.jpg', '.jpeg', '.png']

export const isImage = (path: string) => {
  for (const suffix of IMAGE_SUFFIX) {
    if (path.endsWith(suffix)) {
      return true
    }
  }
  return false
}

export const conditionMapping = {
  MAX: '上限',
  MIN: '下限'
}

export const conditionColorMapping = {
  MAX: 'primary',
  MIN: 'secondary'
}

export const thumbStyle: Partial<CSSStyleDeclaration> = {
  right: '4px',
  borderRadius: '7px',
  backgroundColor: '#027be3',
  width: '4px',
  opacity: '0.75'
}

export const barStyle: Partial<CSSStyleDeclaration> = {
  right: '2px',
  borderRadius: '9px',
  backgroundColor: '#027be3',
  width: '8px',
  opacity: '0.2'
}

export const whiteThumbStyle: Partial<CSSStyleDeclaration> = {
  right: '4px',
  borderRadius: '7px',
  backgroundColor: '#fff',
  width: '4px',
  opacity: '0.75'
}

export const whiteBarStyle: Partial<CSSStyleDeclaration> = {
  right: '2px',
  borderRadius: '9px',
  backgroundColor: '#fff',
  width: '8px',
  opacity: '0.2'
}
