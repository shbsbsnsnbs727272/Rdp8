const twilio = require('twilio');
const readline = require('readline');

// Your Twilio Credentials
const accountSid = 'AC724a92660c58fe465ab4a3feaaf9e334';
const authToken = 'c1548e0e5c3791cab35cad7b1b06756b';

const client = new twilio(accountSid, authToken);

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function showMenu() {
    console.log("\n--- Twilio Free Trial Automation ---");
    console.log("1. Buy a new Twilio number");
    console.log("2. View my Twilio phone number");
    console.log("3. View recent SMS logs");
    console.log("4. Exit");
    rl.question("\nEnter your choice: ", (choice) => {
        handleChoice(choice);
    });
}

async function handleChoice(choice) {
    try {
        switch (choice) {
            case '1':
                console.log("Searching for available US numbers...");
                const available = await client.availablePhoneNumbers('US').local.list({ limit: 1 });
                if (available.length > 0) {
                    const number = await client.incomingPhoneNumbers.create({
                        phoneNumber: available[0].phoneNumber
                    });
                    console.log(XXXINLINECODEXXX1XXXINLINECODEXXX);
                } else {
                    console.log("No numbers available at the moment.");
                }
                showMenu();
                break;

            case '2':
                console.log("Listing your numbers:");
                const numbers = await client.incomingPhoneNumbers.list();
                if (numbers.length === 0) {
                    console.log("No numbers found in this account.");
                } else {
                    numbers.forEach(n => console.log(XXXINLINECODEXXX2XXXINLINECODEXXX));
                }
                showMenu();
                break;

            case '3':
                console.log("Fetching recent SMS logs (last 5):");
                const messages = await client.messages.list({ limit: 5 });
                messages.forEach(m => {
                    console.log(XXXINLINECODEXXX3XXXINLINECODEXXX);
                    console.log(XXXINLINECODEXXX4XXXINLINECODEXXX);
                });
                showMenu();
                break;

            case '4':
                console.log("Exiting...");
                rl.close();
                process.exit(0);
                break;

            default:
                console.log("Invalid choice, please try again.");
                showMenu();
                break;
        }
    } catch (error) {
        console.error("Error occurred:", error.message);
        showMenu();
    }
}

// Start the script
showMenu();
