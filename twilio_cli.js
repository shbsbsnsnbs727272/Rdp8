const readline = require('readline');
const twilio = require('twilio');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

let accountSid = '';
let authToken = '';
let client = null;

function prompt(question) {
  return new Promise(resolve => rl.question(question, answer => resolve(answer.trim())));
}

async function buyNewNumber() {
  try {
    console.log('\nSearching for available phone numbers...');
    // Search for available US phone numbers (you can customize country or type)
    const numbers = await client.availablePhoneNumbers('US').local.list({limit: 5});
    if (numbers.length === 0) {
      console.log('No available numbers found.');
      return;
    }
    console.log('Available numbers:');
    numbers.forEach((num, idx) => {
      console.log(`${idx + 1}. ${num.phoneNumber}`);
    });
    const choice = await prompt('Select a number to buy (enter number): ');
    const index = parseInt(choice, 10) - 1;
    if (index < 0 || index >= numbers.length) {
      console.log('Invalid selection.');
      return;
    }
    const selectedNumber = numbers[index].phoneNumber;
    const purchasedNumber = await client.incomingPhoneNumbers.create({phoneNumber: selectedNumber});
    console.log(`Successfully purchased number: ${purchasedNumber.phoneNumber}`);
  } catch (error) {
    console.error('Error buying new number:', error.message);
  }
}

async function viewMyNumbers() {
  try {
    const numbers = await client.incomingPhoneNumbers.list({limit: 20});
    if (numbers.length === 0) {
      console.log('No Twilio phone numbers found in your account.');
      return;
    }
    console.log('\nYour Twilio phone numbers:');
    numbers.forEach(num => {
      console.log(`- ${num.phoneNumber} (SID: ${num.sid})`);
    });
  } catch (error) {
    console.error('Error fetching phone numbers:', error.message);
  }
}

async function viewRecentSmsLogs() {
  try {
    const messages = await client.messages.list({limit: 10});
    if (messages.length === 0) {
      console.log('No recent SMS messages found.');
      return;
    }
    console.log('\nRecent SMS logs:');
    messages.forEach(msg => {
      console.log(`From: ${msg.from} To: ${msg.to} Status: ${msg.status} Date: ${msg.dateSent}`);
      console.log(`Body: ${msg.body}`);
      console.log('---');
    });
  } catch (error) {
    console.error('Error fetching SMS logs:', error.message);
  }
}

async function main() {
  console.log('Welcome to the Twilio Management CLI\n');

  accountSid = await prompt('Enter your Twilio Account SID: ');
  authToken = await prompt('Enter your Twilio Auth Token: ');

  client = twilio(accountSid, authToken);

  while (true) {
    console.log('\nSelect an option:');
    console.log('1. Buy a new Twilio number');
    console.log('2. View my Twilio phone number(s)');
    console.log('3. View recent SMS logs');
    console.log('4. Exit');

    const choice = await prompt('Enter your choice (1-4): ');

    switch (choice) {
      case '1':
        await buyNewNumber();
        break;
      case '2':
        await viewMyNumbers();
        break;
      case '3':
        await viewRecentSmsLogs();
        break;
      case '4':
        console.log('Exiting. Goodbye!');
        rl.close();
        process.exit(0);
      default:
        console.log('Invalid choice. Please enter a number between 1 and 4.');
    }
  }
}

main();
