import SettingDialog from '../SettingDialog.vue'

describe('SettingDialog', () => {
  it('change theme to click', () => {
    cy.mount(SettingDialog)
    cy.dataCy('dialog-card')
      .should('not.have.class', 'q-dark')
      .then(() => {
        cy.dataCy('theme-toggle')
          .should('have.length', 3)
      })
  })
})
