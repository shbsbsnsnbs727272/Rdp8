const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const os = require('os');

// Configuration
const SCRIPT_DIR = path.dirname(new URL(import.meta.url).pathname);
const BLOCK_SIZE = 512;
const SECTOR_SIZE = 512; // Default logical block size

// Utility Functions
function exec(command, errorMsg = null) {
    try {
        return execSync(command, { encoding: 'utf-8', stdio: ['inherit', 'pipe', 'pipe'] });
    } catch (error) {
        if (errorMsg) console.error(errorMsg);
        throw error;
    }
}

function checkDependencies() {
    const deps = ['cgpt', 'pv'];
    deps.forEach(dep => {
        try {
            execSync(`which ${dep}`);
        } catch (e) {
            console.error(`${dep} needs to be installed first`);
            process.exit(1);
        }
    });

    if (process.getuid && process.getuid() !== 0) {
        console.error("Please run this script with sudo");
        process.exit(1);
    }
}

function getBlockSectors(path) {
    // Simplified logic for image files (assuming 512 bytes per sector)
    if (!fs.existsSync(path)) return 0;
    const stats = fs.statSync(path);
    const bytes = stats.size;
    const rem = bytes % 512;
    let sectors = Math.floor(bytes / 512);
    if (rem !== 0) sectors += 1;
    return sectors;
}

// Partition Table Writing (Port of write_base_table)
function writeBaseTable(target) {
    const block_size = 512; 
    const numsecs = getBlockSectors(target);
    let curr = 32768;

    console.log(`Creating partition table on ${target}...`);

    // Create GPT
    try {
        execSync(`cgpt create ${target}`);
    } catch (e) {
        console.error("Failed to create GPT.");
        throw e;
    }

    // Helper to calculate blocks
    const calcBlocks = (sizeBytes) => {
        let blocks = Math.floor(sizeBytes / block_size);
        if (sizeBytes % block_size > 0) blocks += 1;
        return blocks;
    };

    // Define partitions (mirroring the bash logic)
    const partitions = [
        { id: 11, size: 8388608, type: 'firmware', label: 'RWFW' },
        { id: 6, size: 1, type: 'kernel', label: 'KERN-C' },
        { id: 7, size: 1073741824, type: 'rootfs', label: 'ROOT-C' },
        { id: 9, size: 1, type: 'reserved', label: 'reserved' },
        { id: 10, size: 1, type: 'reserved', label: 'reserved' },
        // Padding calculation logic from bash script for partition 2 start
        { id: 2, size: 67108864, type: 'kernel', label: 'KERN-A', padding: 2062336 },
        { id: 4, size: 67108864, type: 'kernel', label: 'KERN-B' },
        { id: 8, size: 16777216, type: 'data', label: 'OEM' },
        // EFI System partition
        { id: 12, size: 67108864, type: 'efi', label: 'EFI-SYSTEM' },
        { id: 5, size: 4294967296, type: 'rootfs', label: 'ROOT-B' },
        { id: 3, size: 4294967296, type: 'rootfs', label: 'ROOT-A' },
        // STATE (remaining space)
        { id: 1, size: 0, type: 'data', label: 'STATE' } 
    ];

    partitions.forEach(p => {
        // Handle alignment and padding
        if (p.padding) {
            curr += p.padding;
        }
        if ([5, 12].includes(p.id) && (curr % 4096 !== 0)) {
            curr += (4096 - (curr % 4096));
        }

        let blocks;
        if (p.size === 0) {
            // STATE partition uses remaining space minus 24576 sectors
            blocks = Math.floor((numsecs - (curr + 24576)) / block_size);
        } else {
            blocks = calcBlocks(p.size);
        }

        const startBlock = Math.floor(curr / block_size);
        
        execSync(`cgpt add -i ${p.id} -b ${startBlock} -s ${blocks} -t ${p.type} -l "${p.label}" ${target}`);
        
        curr += (blocks * block_size);
    });

    // Set attributes and priorities
    // KERN-A
    execSync(`cgpt add -i 2 -S 0 -T 15 -P 15 ${target}`);
    // KERN-B
    execSync(`cgpt add -i 4 -S 0 -T 15 -P 0 ${target}`);
    // KERN-C
    execSync(`cgpt add -i 6 -S 0 -T 15 -P 0 ${target}`);
    
    // Boot priority for EFI
    execSync(`cgpt boot -p -i 12 ${target}`);
    execSync(`cgpt add -i 12 -B 0 ${target}`);

    execSync(`cgpt show ${target}`);
}

// Image Creation Logic
function createImage(filePath, sizeGB) {
    console.log(`Creating ${sizeGB}GB disk image at ${filePath}...`);
    // Seek creates a sparse file
    execSync(`dd if=/dev/zero of="${filePath}" bs=1G seek=${sizeGB} count=0`);
}

// Partition Copying Logic
function copyPartitions(sourceImg, targetImg) {
    console.log("Copying partitions...");
    
    // Setup loop devices
    // Note: In a production script, you would need to find free loop devices or use losetup -f
    // For this example, we assume /dev/loop0 and /dev/loop1 are free or handle cleanup.
    // We will use direct partition access syntax for loop devices (e.g. /dev/loop0p1)
    
    const sourceLoop = execSync('losetup --show -fP ' + sourceImg).toString().trim();
    const targetLoop = execSync('losetup --show -fP ' + targetImg).toString().trim();
    
    // Refresh partition tables
    execSync(`partprobe ${sourceLoop}`);
    execSync(`partprobe ${targetLoop}`);

    // Mapping from Target Partition ID to Source logic
    // 2 <- 4, 5 <- 3, 7 <- rootc.img, 12 <- efi.img, others <- same ID
    const specialCases = {
        2: { srcPart: 4 },
        5: { srcPart: 3 },
        7: { srcFile: path.join(SCRIPT_DIR, 'rootc.img') },
        12: { srcFile: path.join(SCRIPT_DIR, 'efi_secure.img') } // Assuming secure boot
    };

    const skipParts = [6, 9, 10, 11];

    try {
        for (let i = 1; i <= 12; i++) {
            if (skipParts.includes(i)) continue;

            let sourcePath = '';
            let size = 0;

            if (specialCases[i]) {
                if (specialCases[i].srcPart) {
                    sourcePath = `${sourceLoop}p${specialCases[i].srcPart}`;
                    // Get size in sectors via cgpt
                    const output = execSync(`cgpt show -i ${specialCases[i].srcPart} -s ${sourceLoop}`).toString();
                    size = parseInt(output.trim()) * 512;
                } else if (specialCases[i].srcFile) {
                    if (!fs.existsSync(specialCases[i].srcFile)) {
                        console.warn(`Skipping partition ${i}: ${specialCases[i].srcFile} not found.`);
                        continue;
                    }
                    sourcePath = specialCases[i].srcFile;
                    size = fs.statSync(sourcePath).size;
                }
            } else {
                sourcePath = `${sourceLoop}p${i}`;
                const output = execSync(`cgpt show -i ${i} -s ${sourceLoop}`).toString();
                size = parseInt(output.trim()) * 512;
            }

            const destPart = `${targetLoop}p${i}`;
            
            console.log(`Writing partition ${i} (${(size / 1024 / 1024).toFixed(2)} MB)...`);
            
            // Using dd and pv
            // dd if=src | pv -s size | dd of=dest
            try {
                execSync(`dd if="${sourcePath}" bs=1M 2>/dev/null | pv -s ${size} -N "${i}" | dd of="${destPart}" bs=1M 2>/dev/null`);
            } catch (e) {
                console.error(`Error writing partition ${i}`);
                // Continue to next partition or cleanup
            }
        }
    } finally {
        // Cleanup loop devices
        execSync(`losetup -d ${sourceLoop}`);
        execSync(`losetup -d ${targetLoop}`);
    }
}

// Grub Configuration Generator
function generateGrubConfig(targetImgPath) {
    // Determine UUID (using blkid as fallback, though on images might require loopback)
    let img_uuid = "CHANGE_ME_UUID";
    try {
        // We need to mount the image or look at the loop device to get UUID easily
        // For simplicity, we'll just put a placeholder or try basic blkid if user has partition mounted
        const output = execSync(`blkid -s PARTUUID -o value "${targetImgPath}" 2>/dev/null || echo ""`).toString().trim();
        if (output) img_uuid = output;
    } catch (e) {
        // Ignore
    }

    const img_path = targetImgPath; // Simplified path logic

    const config = `menuentry "Brunch" --class "brunch" {
    img_path="${img_path}"
    img_uuid="${img_uuid}"
    search --no-floppy --set=root --file "$img_path"
    loopback loop "$img_path"
    source (loop,12)/efi/boot/settings.cfg
    if [ -z $verbose ] -o [ $verbose -eq 0 ]; then
        linux (loop,7)$kernel boot=local noresume noswap loglevel=7 options=$options chromeos_bootsplash=$chromeos_bootsplash $cmdline_params \\
            cros_secure cros_debug img_uuid="$img_uuid" img_path="$img_path" \\
            console= vt.global_cursor_default=0 brunch_bootsplash=$brunch_bootsplash quiet
    else
        linux (loop,7)$kernel boot=local noresume noswap loglevel=7 options=$options chromeos_bootsplash=$chromeos_bootsplash $cmdline_params \\
            cros_secure cros_debug img_uuid="$img_uuid" img_path="$img_path"
    fi
    initrd (loop,7)/lib/firmware/amd-ucode.img (loop,7)/lib/firmware/intel-ucode.img (loop,7)/initramfs.img
}

menuentry "Brunch settings" --class "brunch-settings" {
    img_path="${img_path}"
    img_uuid="${img_uuid}"
    search --no-floppy --set=root --file "$img_path"
    loopback loop "$img_path"
    source (loop,12)/efi/boot/settings.cfg
    linux (loop,7)/kernel boot=local noresume noswap loglevel=7 options= chromeos_bootsplash= edit_brunch_config=1 \\
        cros_secure cros_debug img_uuid="$img_uuid" img_path="$img_path"
    initrd (loop,7)/lib/firmware/amd-ucode.img (loop,7)/lib/firmware/intel-ucode.img (loop,7)/initramfs.img
}`;

    const grubFile = `${targetImgPath}.grub.txt`;
    fs.writeFileSync(grubFile, config);
    console.log(`\nGrub configuration generated at: ${grubFile}`);
    console.log("To enable booting, add the contents of this file to your grub configuration.");
}

// Main Execution
async function main() {
    checkDependencies();

    const args = process.argv.slice(2);
    
    // Argument Parsing
    let source = '';
    let destination = '';
    let imageSize = 14; // Default GB
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '-src' || args[i] === '--source') {
            source = args[++i];
        } else if (args[i] === '-dst' || args[i] === '--destination') {
            destination = args[++i];
        } else if (args[i] === '-s' || args[i] === '--size') {
            imageSize = parseInt(args[++i]);
        }
    }

    if (!source || !destination) {
        console.log("Usage: node chromeos_install.js -src <recovery_image.bin> -dst <output.img> [-s <size_in_GB>]");
        process.exit(1);
    }

    if (!fs.existsSync(source)) {
        console.error(`Source image not found: ${source}`);
        process.exit(1);
    }

    // Validate source is ChromeOS image (basic check)
    // The bash script checks magic bytes '33c0fa8e' and cgpt structure. 
    // We'll rely on cgpt failing later if it's invalid, or do a basic check.
    try {
        execSync(`cgpt show ${source}`);
    } catch (e) {
        console.error("Source does not appear to be a valid ChromeOS image.");
        process.exit(1);
    }

    console.log(`Starting Dual Boot Image Creation...`);
    console.log(`Source: ${source}`);
    console.log(`Destination: ${destination}`);
    console.log(`Size: ${imageSize} GB`);

    try {
        // 1. Create Image File
        createImage(destination, imageSize);

        // 2. Write Partition Table
        writeBaseTable(destination);

        // 3. Install/Copy Partitions
        copyPartitions(source, destination);

        // 4. Generate Grub Config
        generateGrubConfig(destination);

        console.log("\nProcess completed successfully.");
    } catch (error) {
        console.error("\nInstallation failed:", error.message);
        process.exit(1);
    }
}

main();
