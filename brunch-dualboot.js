#!/usr/bin/env node
"use strict";

const { execSync, spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

function run(cmd, opts = {}) {
  console.log(`> ${cmd}`);
  execSync(cmd, { stdio: "inherit", ...opts });
}

function exists(cmd) {
  try {
    execSync(`which ${cmd}`, { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

function die(msg) {
  console.error(`❌ ${msg}`);
  process.exit(1);
}

/* ------------------ checks ------------------ */

if (process.getuid() !== 0) {
  die("Run this script with sudo");
}

["cgpt", "dd", "losetup", "pv"].forEach(cmd => {
  if (!exists(cmd)) die(`${cmd} is required`);
});

/* ------------------ args ------------------ */

const args = process.argv.slice(2);
let source, destination, size = 14;

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--source":
    case "-src":
      source = args[++i];
      break;
    case "--destination":
    case "-dst":
      destination = args[++i];
      break;
    case "--size":
    case "-s":
      size = parseInt(args[++i], 10);
      break;
  }
}

if (!source || !destination) {
  die("Usage: sudo node brunch-dualboot.js -src recovery.bin -dst chromeos.img [-s 14]");
}

if (!fs.existsSync(source)) die("Recovery image not found");

/* ------------------ image creation ------------------ */

const fullpath = path.resolve(destination);

console.log(`📦 Creating ${size}GB image: ${fullpath}`);
run(`dd if=/dev/zero of="${fullpath}" bs=1G seek=${size} count=0`);

/* ------------------ partition table ------------------ */

console.log("🧱 Creating GPT layout");
run(`cgpt create "${fullpath}"`);

/* Example minimal GPT layout (Brunch-compatible) */
run(`cgpt add -i 12 -t efi -s 131072 -l EFI-SYSTEM "${fullpath}"`);
run(`cgpt add -i 7  -t kernel -s 131072 -l KERN-C "${fullpath}"`);
run(`cgpt add -i 3  -t rootfs -s 8388608 -l ROOT-A "${fullpath}"`);
run(`cgpt add -i 5  -t rootfs -s 8388608 -l ROOT-B "${fullpath}"`);
run(`cgpt add -i 1  -t data   -s 0        -l STATE "${fullpath}"`);

/* ------------------ loop devices ------------------ */

console.log("🔁 Mapping loop devices");

const srcLoop = execSync(`losetup --show -fP "${source}"`).toString().trim();
const dstLoop = execSync(`losetup --show -fP "${fullpath}"`).toString().trim();

/* ------------------ copy partitions ------------------ */

function copyPart(src, dst) {
  run(`dd if="${src}" bs=4M status=progress | dd of="${dst}" bs=4M`);
}

console.log("📂 Copying partitions");

copyPart(`${srcLoop}p3`, `${dstLoop}p3`); // ROOT-A
copyPart(`${srcLoop}p5`, `${dstLoop}p5`); // ROOT-B
copyPart(`${srcLoop}p12`, `${dstLoop}p12`); // EFI

/* ------------------ cleanup ------------------ */

run(`losetup -d "${srcLoop}"`);
run(`losetup -d "${dstLoop}"`);

/* ------------------ grub config ------------------ */

const grubCfg = `
menuentry "Brunch ChromeOS" {
  loopback loop ${fullpath}
  linux (loop,7)/kernel boot=local noresume noswap cros_debug
  initrd (loop,7)/initramfs.img
}
`;

fs.writeFileSync(`${fullpath}.grub.txt`, grubCfg);

console.log("✅ Done!");
console.log(`📄 GRUB config written to ${fullpath}.grub.txt`);
