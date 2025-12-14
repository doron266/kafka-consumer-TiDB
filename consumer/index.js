const { Kafka } = require('kafkajs');

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

const extractValues = (row) =>
    Object.fromEntries(
        Object.entries(row).map(([key, meta]) => [key, meta?.v])
    );

const parseTiCDCMessage = (parsed) => {
    if (parsed.c) {
        return { operation: 'INSERT', data: extractValues(parsed.c) };
    }
    if (parsed.u) {
        return { operation: 'UPDATE', data: extractValues(parsed.u) };
    }
    if (parsed.d) {
        return { operation: 'DELETE', data: extractValues(parsed.d) };
    }
    return { operation: 'UNKNOWN', data: parsed };
};

/**
 * Main runner
 */
const run = async () => {
    console.log('Starting CDC Consumer...');

    let connected = false;
    let retries = 0;

    while (!connected && retries < 30) {
        try {
            await consumer.connect();
            connected = true;
            console.log('Connected to Kafka');
        } catch (err) {
            retries++;
            console.log(`Kafka not ready, retrying in 5s... (${retries}/30)`);
            await sleep(5000);
        }
    }

    if (!connected) {
        console.error('Failed to connect to Kafka after 30 attempts');
        process.exit(1);
    }

    await consumer.subscribe({ topic: 'users', fromBeginning: true });
    await consumer.subscribe({ topic: 'orders', fromBeginning: true });

    console.log('Subscribed to topics: users, orders');

    await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {
            const rawValue = message.value?.toString();
            if (!rawValue) return;

            try {
                const parsed = JSON.parse(rawValue);

                /**
                 * USERS CDC
                 */
                if (topic === 'users') {
                    const { operation, data } = parseTiCDCMessage(parsed);

                    const logEntry = {
                        timestamp: new Date().toISOString(),
                        source: 'ticdc',
                        topic,
                        partition,
                        offset: message.offset,
                        table: 'users',
                        operation,
                        data
                    };

                    console.log(JSON.stringify(logEntry));
                }

                /**
                 * ORDERS CDC (generic passthrough)
                 */
                else if (topic === 'orders') {
                    const logEntry = {
                        timestamp: new Date().toISOString(),
                        source: 'ticdc',
                        topic,
                        partition,
                        offset: message.offset,
                        data: parsed
                    };

                    console.log(JSON.stringify(logEntry));
                }

            } catch (err) {
                console.error(JSON.stringify({
                    timestamp: new Date().toISOString(),
                    error: 'JSON_PARSE_ERROR',
                    message: err.message,
                    topic,
                    partition,
                    offset: message.offset,
                    rawValue: rawValue.slice(0, 200)
                }));
            }
        }
    });
};

/**
 * Graceful shutdown (Docker / K8s friendly)
 */
const shutdown = async (signal) => {
    console.log(`Received ${signal}, shutting down...`);
    try {
        await consumer.disconnect();
    } finally {
        process.exit(0);
    }
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

run().catch(err => {
    console.error('Fatal consumer error:', err);
    process.exit(1);
});

