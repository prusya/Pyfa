type = "passive"
def handler(fit, src, context):
    fit.modules.filteredItemBoost(lambda mod: mod.item.requiresSkill("Capital Capacitor Emission Systems"), "powerTransferAmount", src.getModifiedItemAttr("shipBonusForceAuxiliaryC1"), skill="Caldari Carrier")
    fit.modules.filteredItemBoost(lambda mod: mod.item.requiresSkill("Capital Shield Emission Systems"), "shieldBonus", src.getModifiedItemAttr("shipBonusForceAuxiliaryC1"), skill="Caldari Carrier")