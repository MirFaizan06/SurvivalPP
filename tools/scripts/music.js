// Boss fight music for the four main story bosses (six). The track starts for every player near the boss as soon as the boss exists
// (ritual, journal quest or /summon), repeats while the fight lasts, and stops when the boss dies or the player walks away.
import { world, system } from '@minecraft/server';
import { NS, safe } from './util.js';

/** boss entity id -> { sound definition id, track length in seconds, volume } */
const TRACKS = {
    [`${NS}:veiled_blossom`]: { id: 'ecr.music.veiled_blossom', secs: 114, volume: 0.85 },
    [`${NS}:eclipse_sovereign`]: { id: 'ecr.music.eclipse_sovereign', secs: 123, volume: 0.85 },
    [`${NS}:frost_cantor`]: { id: 'ecr.music.frost_cantor', secs: 114, volume: 0.85 },
    [`${NS}:mire_lantern`]: { id: 'ecr.music.mire_lantern', secs: 142, volume: 0.85 },
    [`${NS}:cinder_bride`]: { id: 'ecr.music.cinder_bride', secs: 108, volume: 0.9 },
    [`${NS}:ashen_groom`]: { id: 'ecr.music.ashen_groom', secs: 130, volume: 0.9 },
};
const RANGE = 64;
const LEAVE = 90;
/** boss id -> Map(player id -> tick at which the track has to be restarted) */
const playing = new Map();

function silence(p, track) {
    safe(() => p.runCommand(`stopsound @s ${track.id}`), 'stopMusic');
}

/** call every few ticks while the boss is alive */
export function tickMusic(boss) {
    const track = TRACKS[boss.typeId];
    if (!track) return;
    const now = system.currentTick;
    let m = playing.get(boss.id);
    if (!m) { m = new Map(); playing.set(boss.id, m); }
    for (const p of world.getAllPlayers()) {
        if (p.dimension.id !== boss.dimension.id) {
            if (m.has(p.id)) { silence(p, track); m.delete(p.id); }
            continue;
        }
        const d = Math.hypot(p.location.x - boss.location.x, p.location.z - boss.location.z);
        if (d <= RANGE) {
            if (!m.has(p.id) || now >= m.get(p.id)) {
                safe(() => {
                    p.runCommand('music stop 0.5');                       // fade out the vanilla soundtrack
                    p.playSound(track.id, { volume: track.volume });
                }, 'playMusic');
                m.set(p.id, now + track.secs * 20 + 20);
            }
        } else if (d > LEAVE && m.has(p.id)) {
            silence(p, track);
            m.delete(p.id);
        }
    }
}

/** call when the boss dies or is removed */
export function stopMusic(boss) {
    const track = TRACKS[boss.typeId];
    const m = playing.get(boss.id);
    if (!track || !m) return;
    for (const p of world.getAllPlayers()) if (m.has(p.id)) silence(p, track);
    playing.delete(boss.id);
}
