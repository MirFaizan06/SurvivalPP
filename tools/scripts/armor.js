// Full-set armour bonuses (refreshed every 2 s, no particles)
import { world, system, EquipmentSlot, EntityComponentTypes } from '@minecraft/server';
import { NS, safe } from './util.js';

const SETS = {
    azurite: [['haste', 0]],
    pyrelite: [['fire_resistance', 0], ['strength', 0]],
    eclipsite: [['speed', 0], ['night_vision', 0], ['slow_falling', 0], ['resistance', 0], ['water_breathing', 0]],
    sakura: [['speed', 0], ['jump_boost', 0]],
};
/** @type {[EquipmentSlot, string][]} */
const SLOTS = [[EquipmentSlot.Head, 'helmet'], [EquipmentSlot.Chest, 'chestplate'], [EquipmentSlot.Legs, 'leggings'], [EquipmentSlot.Feet, 'boots']];

export function initArmor() {
    system.runInterval(() => {
        for (const p of world.getAllPlayers()) {
            safe(() => {
                const eq = p.getComponent(EntityComponentTypes.Equippable);
                let mat;
                for (const [slot, kind] of SLOTS) {
                    const it = eq.getEquipment(slot);
                    const m = it && new RegExp(`^${NS}:(azurite|pyrelite|eclipsite|sakura)_${kind}$`).exec(it.typeId);
                    if (!m) return;
                    if (mat && mat !== m[1]) return;
                    mat = m[1];
                }
                for (const [eff, amp] of SETS[mat]) p.addEffect(eff, eff === 'night_vision' ? 320 : 100, { amplifier: amp, showParticles: false });
            }, 'armorSet');
        }
    }, 40);
}
