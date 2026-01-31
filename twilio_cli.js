const twilio = require('twilio');

// Get command-line arguments
const [choice, accountSid, authToken] = process.argv.slice(2);

const client = new twilio(accountSid, authToken);

async function buyNewNumber() {
    try {
        const numbers = await client.availablePhoneNumbers('US').local.list();
        if (numbers.length > 0) {
            const newNumber = numbers[0].phoneNumber; // Get the first available number
            const purchasedNumber = await client.incomingPhoneNumbers.create({
                phoneNumber: newNumber,
            });
            console.log(Successfully purchased new Twilio number: ${purchasedNumber.phoneNumber});
        } else {
            console.log('No available phone numbers found.');
        }
    } catch (error) {
        console.error('Error purchasing new number:', error.message);
    }
}

async function viewMyPhoneNumbers() {
    try {
        const phoneNumbers = await client.incomingPhoneNumbers.list();
        console.log('Your Twilio Phone Numbers:');
        phoneNumbers.forEach(number => {
            console.log(- ${number.phoneNumber});
        });
    } catch (error) {
        console.error('Error retrieving phone numbers:', error.message);
    }
}

async function viewRecentSmsLogs() {
    try {
        const messages = await client.messages.list({ limit: 10 });
        console.log('Recent SMS Logs:');
        messages.forEach(message => {
            console.log(- From: ${message.from}, To: ${message.to}, Body: "${message.body}", Status: ${message.status});
        });
    } catch (error) {
        console.error('Error retrieving SMS logs:', error.message);
    }
}

// Main function to handle user input
async function main() {
    switch (choice) {
        case '1':
            await buyNewNumber();
            break;
        case '2':
            await viewMyPhoneNumbers();
            break;
        case '3':
            await viewRecentSmsLogs();
            break;
        case '4':
            console.log('Exiting...');
            process.exit(0);
            break;
        default:
            console.log('Invalid choice. Please select a valid option.');
    }
}

main().catch(error => {
    console.error('An error occurred:', error.message);
});
