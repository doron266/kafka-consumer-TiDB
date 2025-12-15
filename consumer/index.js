const { Kafka } = require('kafkajs');
const log4js = require('log4js');

/**
 * Kafka client
 */
const kafka = new Kafka({
    clientId: 'cdc-consumer',
    brokers: (process.env.KAFKA_BROKERS || 'kafka:9092').split(',')
});

const consumer = kafka.consumer({
    groupId: 'cdc-consumer-group'
});

/**
 * Helpers
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const isEmptyBuffer = (buf) => {
    if (!buf || buf.length === 0) return true;
    // Buffer full of null bytes
    return buf.every(byte => byte === 0);
};

const extractValues = (row) =>
    Object.fromEntries(
        Object.entries(row).map(([key, meta]) => [key, meta?.v])
    );

const parseTiCDCMessage = (parsed) => {
    if (parsed.c) return { operation: 'INSERT', data: extractValues(parsed.c) };
    if (parsed.u) return { operation: 'UPDATE', data: extractValues(parsed.u) };
    if (parsed.d) return { operation: 'DELETE', data: extractValues(parsed.d) };
    return { operation: 'UNKNOWN', data: parsed };
};

/**
 * Main runner
 */
const run = async () => {
    console.log('Starting CDC Consumer...');

    let retries = 0;
    while (retries < 30) {
        try {
            await consumer.connect();
            console.log('Connected to Kafka');
            break;
        } catch {
            retries++;
            console.log(`Kafka not ready, retrying in 5s... (${retries}/30)`);
            await sleep(5000);
        }
    }

    if (retries === 30) {
        console.error('Failed to connect to Kafka');
        process.exit(1);
    }

    await consumer.assign({ topic: 'users', fromBeginning: true });
    await consumer.assign({ topic: 'orders', fromBeginning: true });

    console.log('Subscribed to topics: users, orders');

    await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {

            /**
             * 1️⃣ Empty / tombstone / binary-only messages
             */
            if (isEmptyBuffer(message.value)) {
                console.log(JSON.stringify({
                    timestamp: new Date().toISOString(),
                    topic,
                    partition,
                    offset: message.offset,
                    skipped: true,
                    reason: 'EMPTY_OR_TOMBSTONE'
                }));
                return;
            }

            /**
             * 2️⃣ Convert to string & sanitize
             */
            const raw = message.value.toString('utf8');
            const cleaned = raw.replace(/\0/g, '').trim();

            /**
             * 3️⃣ Still not JSON? Skip
             */
            if (!cleaned.startsWith('{')) {
                console.log(JSON.stringify({
                    timestamp: new Date().toISOString(),
                    topic,
                    partition,
                    offset: message.offset,
                    skipped: true,
                    reason: 'NON_JSON',
                    preview: cleaned.slice(0, 100)
                }));
                return;
            }

            /**
             * 4️⃣ Parse JSON
             */
            let parsed;
            try {
                parsed = JSON.parse(cleaned);
            } catch (err) {
                console.error(JSON.stringify({
                    timestamp: new Date().toISOString(),
                    topic,
                    partition,
                    offset: message.offset,
                    error: 'JSON_PARSE_ERROR',
                    message: err.message
                }));
                return;
            }

            /**
             * 5️⃣ Topic-specific handling
             */
            if (topic === 'users') {
                const { operation, data } = parseTiCDCMessage(parsed);

                console.log(JSON.stringify({
                    timestamp: new Date().toISOString(),
                    source: 'ticdc',
                    topic,
                    partition,
                    offset: message.offset,
                    table: 'users',
                    operation,
                    data
                }));
            }

            if (topic === 'orders') {
                console.log(JSON.stringify({
                    timestamp: new Date().toISOString(),
                    source: 'ticdc',
                    topic,
                    partition,
                    offset: message.offset,
                    data: parsed
                }));
            }
        }
    });
};

/**
 * Graceful shutdown
 */
const shutdown = async (signal) => {
    console.log(`Received ${signal}, shutting down...`);
    await consumer.disconnect();
    process.exit(0);
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

run().catch(err => {
    console.error('Fatal consumer error:', err);
    process.exit(1);
});
