// Procedural Jacaranda trees used when a sapling grows (world generation uses the data-driven tree features)
import { BlockPermutation } from '@minecraft/server';
import { NS, safe, rand, randInt } from './util.js';

const REPLACEABLE = new Set(['minecraft:air', 'minecraft:short_grass', 'minecraft:tall_grass', 'minecraft:fern', 'minecraft:large_fern', 'minecraft:snow_layer', 'minecraft:vine']);
const SOIL = new Set(['minecraft:dirt', 'minecraft:grass_block', 'minecraft:podzol', 'minecraft:coarse_dirt', 'minecraft:mud', 'minecraft:moss_block', 'minecraft:dirt_with_roots']);

function line(a, b, cb) {
    const dx = b[0] - a[0], dy = b[1] - a[1], dz = b[2] - a[2];
    const n = Math.max(Math.abs(dx), Math.abs(dy), Math.abs(dz), 1);
    let last = null;
    for (let i = 0; i <= n; i++) {
        const p = [Math.round(a[0] + (dx * i) / n), Math.round(a[1] + (dy * i) / n), Math.round(a[2] + (dz * i) / n)];
        if (last && (last[0] !== p[0] || last[1] !== p[1] || last[2] !== p[2])) cb(p, [p[0] - last[0], p[1] - last[1], p[2] - last[2]]);
        else if (!last) cb(p, [0, 1, 0]);
        last = p;
    }
}

class Tree {
    constructor() {
        this.logs = new Map();   // "x,y,z" -> axis
        this.leaves = new Set();
    }
    log(p, axis) {
        this.logs.set(p.join(','), axis);
    }
    leaf(p) {
        const k = p.join(',');
        if (!this.logs.has(k)) this.leaves.add(k);
    }
    branch(a, b) {
        line(a, b, (p, d) => {
            const ax = Math.abs(d[1]) >= Math.abs(d[0]) && Math.abs(d[1]) >= Math.abs(d[2]) ? 'y' : Math.abs(d[0]) >= Math.abs(d[2]) ? 'x' : 'z';
            this.log(p, ax);
        });
    }
    blob(c, rx, ry, rz, hole = 0.1) {
        for (let dx = -Math.ceil(rx); dx <= Math.ceil(rx); dx++) {
            for (let dy = -Math.ceil(ry); dy <= Math.ceil(ry); dy++) {
                for (let dz = -Math.ceil(rz); dz <= Math.ceil(rz); dz++) {
                    const d = (dx / rx) ** 2 + (dy / ry) ** 2 + (dz / rz) ** 2;
                    if (d <= 1 + (Math.random() - 0.5) * 0.35 && Math.random() > hole) this.leaf([c[0] + dx, c[1] + dy, c[2] + dz]);
                }
            }
        }
    }
    droop(prob, maxLen) {
        const add = [];
        for (const k of this.leaves) {
            const [x, y, z] = k.split(',').map(Number);
            if (this.leaves.has(`${x},${y - 1},${z}`) || this.logs.has(`${x},${y - 1},${z}`)) continue;
            if (Math.random() < prob) {
                const len = randInt(1, maxLen);
                for (let i = 1; i <= len; i++) add.push([x, y - i, z]);
            }
        }
        for (const p of add) this.leaf(p);
    }
}

function weeping() {
    const t = new Tree();
    const h = randInt(6, 8);
    let x = 0, z = 0;
    for (let y = 0; y < h; y++) {
        if (y > 2 && Math.random() < 0.25) x += Math.random() < 0.5 ? 1 : -1;
        if (y > 2 && Math.random() < 0.25) z += Math.random() < 0.5 ? 1 : -1;
        t.log([x, y, z], 'y');
    }
    const top = [x, h - 1, z];
    const n = randInt(2, 4);
    for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2 + rand(-0.5, 0.5);
        const len = randInt(3, 4);
        const end = [top[0] + Math.round(Math.cos(a) * len), top[1] + randInt(0, 2), top[2] + Math.round(Math.sin(a) * len)];
        t.branch([top[0], top[1] - randInt(0, 2), top[2]], end);
        t.blob(end, 3.3, 2.1, 3.3, 0.12);
    }
    t.blob([top[0], top[1] + 1, top[2]], 3.8, 2.6, 3.8, 0.1);
    // flared roots
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) if (Math.random() < 0.6) t.log([dx, 0, dz], dx ? 'x' : 'z');
    t.droop(0.32, 4);
    return t;
}

function round() {
    const t = new Tree();
    const h = randInt(5, 7);
    let x = 0, z = 0;
    for (let y = 0; y < h; y++) {
        if (y >= 2 && y % 2 === 0 && Math.random() < 0.55) x += 1;
        t.log([x, y, z], 'y');
    }
    const top = [x, h - 1, z];
    t.branch(top, [top[0] + 3, top[1] + 1, top[2] + 1]);
    t.branch(top, [top[0] - 3, top[1] + 1, top[2] - 1]);
    t.blob([top[0], top[1] + 1, top[2]], 5.2, 2.4, 5.2, 0.12);
    t.blob([top[0] + 4, top[1] + 1, top[2] + 1], 2.8, 1.8, 2.8, 0.1);
    t.blob([top[0] - 4, top[1] + 1, top[2] - 1], 2.8, 1.8, 2.8, 0.1);
    t.droop(0.16, 3);
    return t;
}

function grand() {
    const t = new Tree();
    const h = randInt(11, 14);
    for (let y = 0; y < h; y++) t.log([0, y, 0], 'y');
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { t.log([dx, 0, dz], dx ? 'x' : 'z'); if (Math.random() < 0.5) t.log([dx, 1, dz], 'y'); }
    const n = 4;
    for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2 + rand(-0.4, 0.4);
        const by = Math.floor(h * rand(0.55, 0.75));
        const len = randInt(4, 5);
        const end = [Math.round(Math.cos(a) * len), by + randInt(2, 3), Math.round(Math.sin(a) * len)];
        t.branch([0, by, 0], end);
        t.blob(end, 3.6, 2.6, 3.6, 0.1);
    }
    t.blob([0, h, 0], 4.6, 3.3, 4.6, 0.08);
    t.droop(0.28, 5);
    return t;
}

function conifer(tall) {
    const t = new Tree();
    const h = tall ? randInt(11, 15) : randInt(7, 10);
    for (let y = 0; y < h; y++) t.log([0, y, 0], 'y');
    const y0 = Math.floor(h * (tall ? 0.28 : 0.32));
    const maxR = tall ? 3.2 : 2.8;
    for (let y = y0; y <= h + 1; y++) {
        const f = (y - y0) / (h + 1 - y0);
        let r = maxR * (1 - f) + (((y - y0) % 2 === 0) ? 0.7 : 0);
        if (y >= h) r = y === h ? 1.2 : 0.4;
        const R = Math.ceil(r);
        for (let dx = -R; dx <= R; dx++) for (let dz = -R; dz <= R; dz++) if (Math.hypot(dx, dz) <= r + 0.15 && (dx !== 0 || dz !== 0 || y > h - 1)) t.leaf([dx, y, dz]);
    }
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) if (Math.random() < 0.5) t.log([dx, 0, dz], dx ? 'x' : 'z');
    return t;
}

function maple(big) {
    const t = new Tree();
    const h = big ? randInt(7, 10) : randInt(4, 6);
    let x = 0;
    for (let y = 0; y < h; y++) {
        if (big && y > 3 && Math.random() < 0.3) x += Math.random() < 0.5 ? 1 : -1;
        t.log([x, y, 0], 'y');
    }
    const top = [x, h - 1, 0];
    if (big) {
        const n = randInt(2, 3);
        for (let i = 0; i < n; i++) {
            const a = (i / n) * Math.PI * 2 + rand(0, 1);
            const end = [top[0] + Math.round(Math.cos(a) * 3), top[1] + randInt(0, 1), Math.round(Math.sin(a) * 3)];
            t.branch([top[0], top[1] - 1, 0], end);
            t.blob(end, 3, 2.4, 3, 0.1);
        }
        t.blob([top[0], top[1] + 2, 0], 4.8, 3.6, 4.8, 0.08);
    } else {
        t.blob([top[0], top[1] + 1, 0], 3.3, 2.8, 3.3, 0.08);
    }
    t.droop(0.06, 2);
    return t;
}

function acacia(umbrella) {
    const t = new Tree();
    const h1 = randInt(3, 4);
    for (let y = 0; y < h1; y++) t.log([0, y, 0], 'y');
    const dx = Math.random() < 0.5 ? 1 : -1;
    let x = 0, y = h1;
    for (let i = 0; i < 2; i++) { x += dx; t.log([x, y, 0], 'x'); y += 1; t.log([x, y - 1, 0], 'y'); }
    const top = [x, y, 0];
    t.log(top, 'y');
    if (umbrella) {
        t.blob([top[0], top[1] + 1, top[2]], 5.4, 1.5, 5.4, 0.1);
    } else {
        t.blob([top[0], top[1] + 1, top[2]], 3.8, 1.3, 3.8, 0.06);
        const bx = -dx * 3;
        t.branch([0, h1 - 1, 0], [bx, h1 + 1, 0]);
        t.blob([bx, h1 + 2, 0], 3.2, 1.2, 3.2, 0.08);
    }
    return t;
}

function willow() {
    const t = new Tree();
    const h = randInt(5, 7);
    for (let y = 0; y < h; y++) t.log([0, y, 0], 'y');
    const top = [0, h - 1, 0];
    const n = randInt(3, 4);
    for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2 + rand(0, 1);
        const end = [Math.round(Math.cos(a) * 3), top[1] + randInt(0, 1), Math.round(Math.sin(a) * 3)];
        t.branch([0, top[1] - 1, 0], end);
        t.blob(end, 2.6, 1.8, 2.6, 0.1);
    }
    t.blob([0, top[1] + 1, 0], 3.6, 2.2, 3.6, 0.08);
    t.droop(0.6, 7);
    return t;
}

const SPECIES = {
    jacaranda: [weeping, weeping, weeping, round, round, grand],
    frostpine: [() => conifer(false), () => conifer(false), () => conifer(true)],
    amberwood: [() => maple(true), () => maple(true), () => maple(false)],
    sunwood: [() => acacia(false), () => acacia(true)],
    mireweep: [willow, willow, willow],
};

function canGrowHere(block) {
    const below = safe(() => block.below());
    return !!below && SOIL.has(below.typeId);
}

export function woodOf(typeId) {
    const m = /^ecr:([a-z]+)_sapling$/.exec(typeId);
    return m ? m[1] : undefined;
}

export function growTree(sapling) {
    const r = safe(() => {
        const w = woodOf(sapling.typeId);
        if (!sapling.isValid || !w || !SPECIES[w]) return 'invalid';
        if (!canGrowHere(sapling)) return 'soil';
        const list = SPECIES[w];
        const tree = list[Math.floor(Math.random() * list.length)]();
        const dim = sapling.dimension;
        const ox = sapling.location.x, oy = sapling.location.y, oz = sapling.location.z;
        const ok = (id) => REPLACEABLE.has(id) || id === sapling.typeId;
        // the trunk base must be free; everything else is placed wherever there is room
        for (const [k] of tree.logs) {
            const [x, y, z] = k.split(',').map(Number);
            if (x === 0 && z === 0 && y <= 3) {
                const b = safe(() => dim.getBlock({ x: ox + x, y: oy + y, z: oz + z }));
                if (!b) return 'unloaded';
                if (!ok(b.typeId)) return 'space';
            }
        }
        const face = { y: 'up', x: 'east', z: 'north' };
        for (const [k, axis] of tree.logs) {
            const [x, y, z] = k.split(',').map(Number);
            const b = safe(() => dim.getBlock({ x: ox + x, y: oy + y, z: oz + z }));
            if (b && ok(b.typeId)) b.setPermutation(BlockPermutation.resolve(`${NS}:${w}_log`, { 'minecraft:block_face': face[axis] }));
        }
        for (const k of tree.leaves) {
            const [x, y, z] = k.split(',').map(Number);
            const b = safe(() => dim.getBlock({ x: ox + x, y: oy + y, z: oz + z }));
            if (b && ok(b.typeId)) b.setPermutation(BlockPermutation.resolve(`${NS}:${w}_leaves`, { 'ecr:persistent': 0 }));
        }
        safe(() => dim.playSound('random.pop', { x: ox, y: oy, z: oz }));
        return 'ok';
    }, 'growTree');
    return r || 'error';
}
