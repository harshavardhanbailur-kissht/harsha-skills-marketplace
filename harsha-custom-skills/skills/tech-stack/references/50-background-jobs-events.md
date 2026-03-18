# Background Jobs & Event-Driven Architecture Reference

<!-- PRICING_STABILITY: REVIEWED_2026_03 -->

## Executive Summary

Background job systems and event-driven architectures enable scalable, decoupled applications by processing work asynchronously. Choose between lightweight queues (BullMQ, Celery) for <1M events/day, managed platforms (Temporal, Inngest) for reliability at scale, and message brokers (Kafka, RabbitMQ) for complex event streams. Key patterns include outbox for consistency, saga for distributed transactions, and CQRS for separation of concerns. Most teams start self-hosted for cost, migrate to managed services around 10M+ daily events for operational simplicity.

---

## Table of Contents

1. [Job Queue Systems](#job-queue-systems)
2. [Message Brokers](#message-brokers)
3. [Event-Driven Patterns](#event-driven-patterns)
4. [Decision Matrices](#decision-matrices)
5. [Real-World Architectures](#real-world-architectures)
6. [Performance Benchmarks](#performance-benchmarks)
7. [Cost Analysis](#cost-analysis)
8. [Implementation Considerations](#implementation-considerations)

---

## Job Queue Systems

Job queues are designed for discrete work items: emails, image processing, report generation, webhook deliveries.

### Queue System Comparison Matrix

| System | Language | License | Self-Hosted Cost | Managed Cost | Best For | Throughput | Latency | Durability |
|--------|----------|---------|-----------------|--------------|----------|-----------|---------|-----------|
| **BullMQ** | Node.js | MIT | Free (Redis only) | N/A | Node.js microservices | 10K/sec | <100ms | Excellent |
| **Celery** | Python | BSD | Free (broker cost) | N/A | Python async tasks | 100K+/sec | <100ms | Excellent |
| **Sidekiq** | Ruby | AGPL/Commercial | Free (Redis only) | $99-999/mo | Ruby Rails apps | 10K/sec | <100ms | Excellent |
| **RQ** | Python | BSD | Free (Redis) | N/A | Simple Python tasks | 1K/sec | <100ms | Good |
| **Resque** | Ruby | MIT | Free (Redis) | N/A | Simple Ruby tasks | 1K/sec | <100ms | Good |
| **Temporal Cloud** | Multi-lang | Commercial | $500+/mo | $100/mo min | Long-running workflows | 100K+/sec | <1s | Perfect |
| **Inngest** | Multi-lang | Commercial | N/A | $25/mo starter | Serverless/functions | 1M+/month | <100ms | Excellent |
| **Trigger.dev** | Node.js/Python | Commercial | N/A | $10/mo starter | Serverless workflows | 100K/month | <100ms | Excellent |
| **AWS Lambda** | Multi-lang | Commercial | N/A | $0.20/M invokes | Serverless processing | 1000 concurrent | <1s | Excellent |
| **Google Cloud Tasks** | Multi-lang | Commercial | N/A | $0.10/M calls | Lightweight task dispatch | 100K/day | <100ms | Good |
| **AWS SQS** | Multi-lang | Commercial | N/A | $0.40/M requests | Decoupled services | 3K/sec | <100ms | Excellent |

### Job Queue System Deep Dive

#### BullMQ (Node.js)
- **Language**: TypeScript/JavaScript
- **Architecture**: Redis-backed queue with worker processes
- **Pricing**: Free (pay for Redis: $15-100+/mo depending on size)
- **Throughput**: 5,000-10,000 jobs/second per queue
- **Latency**: 50-100ms average
- **Best For**:
  - Node.js/TypeScript microservices
  - Real-time task processing
  - Email/notification delivery
  - Image/video processing
- **Pros**:
  - Excellent TypeScript support
  - Built-in rate limiting
  - Job priority and delay
  - Metrics and monitoring
  - Active maintenance
- **Cons**:
  - Redis dependency
  - Single-server throughput limits
  - Limited cross-language support
- **Scalability**: Horizontal via Redis clustering
- **Setup Time**: 2-4 hours
- **Example Cost**: 10M jobs/month = Redis $50/mo + compute

```javascript
// Example: BullMQ setup
import Queue from 'bull';

const emailQueue = new Queue('emails', {
  redis: { host: '127.0.0.1', port: 6379 }
});

// Producer
await emailQueue.add(
  { to: 'user@example.com', template: 'welcome' },
  { delay: 5000, attempts: 3, backoff: { type: 'exponential', delay: 2000 } }
);

// Consumer
emailQueue.process(5, async (job) => {
  await sendEmail(job.data);
});

emailQueue.on('completed', (job) => {
  console.log(`Job ${job.id} completed`);
});
```

#### Celery (Python)
- **Language**: Python
- **Architecture**: Distributed task queue with multiple broker backends
- **Pricing**: Free (pay for broker: Redis $15/mo, RabbitMQ $19/mo)
- **Throughput**: 50,000-100,000+ tasks/second
- **Latency**: 50-200ms average
- **Best For**:
  - Python/Django applications
  - Data processing pipelines
  - ML model training jobs
  - Large-scale batch processing
- **Pros**:
  - Massive throughput capability
  - Multiple broker options (Redis, RabbitMQ, Kafka)
  - Excellent for long-running tasks
  - Rich task management features
  - Celery Beat for scheduling
- **Cons**:
  - Complex configuration
  - Steep learning curve
  - Python-only
  - Memory overhead
- **Scalability**: Horizontal across worker nodes
- **Setup Time**: 4-8 hours
- **Example Cost**: 100M tasks/month = RabbitMQ $50/mo + compute

```python
# Example: Celery setup
from celery import Celery, group, chain
import time

app = Celery('tasks', broker='redis://localhost:6379')

@app.task(bind=True, max_retries=3)
def send_email(self, to, template):
    try:
        # Send email logic
        time.sleep(1)
        return f"Email sent to {to}"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

@app.task
def generate_report(user_id):
    return f"Report for user {user_id}"

# Producer: Immediate task
send_email.delay('user@example.com', 'welcome')

# Producer: Scheduled
from celery.schedules import crontab
app.conf.beat_schedule = {
    'generate-daily-report': {
        'task': 'tasks.generate_report',
        'schedule': crontab(hour=0, minute=0),
    },
}

# Producer: Chain/workflow
workflow = chain(
    send_email.s('user@example.com', 'welcome'),
    generate_report.s('user123')
)
workflow.apply_async()
```

#### Sidekiq (Ruby)
- **Language**: Ruby
- **Architecture**: Redis-backed worker pool (uses Celluloid threading)
- **Pricing**:
  - Open Source: Free
  - Sidekiq Pro: $99/month (real-time updates, queue prioritization)
  - Sidekiq Enterprise: $999/month (encryption, rate limiting)
- **Throughput**: 5,000-10,000 jobs/second
- **Latency**: 50-100ms
- **Best For**:
  - Ruby on Rails applications
  - Real-time notifications
  - Webhook delivery
  - Mailer jobs
- **Pros**:
  - Tight Rails integration
  - Simple DSL
  - Excellent monitoring UI
  - Active maintenance
  - Clear upgrade path
- **Cons**:
  - Ruby-only
  - Single JVM process (though multithreaded)
  - Redis dependency
- **Scalability**: Horizontal across processes/servers
- **Setup Time**: 1-2 hours
- **Example Cost**: 10M jobs/month = Free + Redis $50/mo + compute

```ruby
# Example: Sidekiq setup
class SendEmailWorker
  include Sidekiq::Worker
  sidekiq_options retry: 3, dead: true

  def perform(user_id, template)
    user = User.find(user_id)
    UserMailer.send_template(user, template).deliver_later
  end
end

# Producer
SendEmailWorker.perform_async(user.id, 'welcome')
SendEmailWorker.perform_in(5.minutes, user.id, 'reminder')

# Scheduled job
class GenerateReportWorker
  include Sidekiq::Worker
  sidekiq_options lock: { type: :until_executed }

  def perform
    Report.generate_daily
  end
end

# In config/sidekiq.yml
:schedule:
  generate_daily_report:
    cron: '0 0 * * *'
    class: GenerateReportWorker
```

#### Temporal Cloud / Temporal.io
- **Language**: Multi-language (Java, Go, Python, TypeScript, .NET)
- **Architecture**: Distributed workflow orchestration platform
- **Pricing**:
  - Self-hosted: Free (ops cost)
  - Temporal Cloud: $100/month minimum + $0.10 per 1000 actions
  - 1M actions/month = ~$200
  - 100M actions/month = ~$10,000
- **Throughput**: 100,000+ actions/second
- **Latency**: 500ms-1s
- **Best For**:
  - Long-running distributed workflows
  - Saga pattern implementation
  - Complex multi-step processes
  - Microservice orchestration
  - Durable execution
- **Pros**:
  - Guarantees: exactly-once execution
  - Replay capability for debuggability
  - Language-agnostic
  - Handles failures, retries, timeouts
  - Audit trail of all execution
  - Scalable to massive volumes
- **Cons**:
  - Steeper learning curve
  - Overkill for simple tasks
  - Minimum cost ($100/mo)
  - Operational complexity for self-hosted
- **Scalability**: Unlimited horizontal scaling
- **Setup Time**: 8-16 hours
- **Example Cost**: Order processing platform = $500-2000/mo depending on volume

```typescript
// Example: Temporal workflow
import * as wf from '@temporalio/workflow';
import * as activities from './activities';

export async function orderProcessingWorkflow(order: Order) {
  const payment = await wf.executeActivity(
    activities.processPayment,
    { orderId: order.id, amount: order.total },
    { startToCloseTimeout: '10 minutes', retry: { maxAttempts: 3 } }
  );

  if (!payment.success) {
    throw new Error('Payment failed');
  }

  await wf.executeActivity(activities.reserveInventory, {
    items: order.items,
  });

  const shipment = await wf.executeActivity(
    activities.createShipment,
    { orderId: order.id }
  );

  await wf.sleep('5 days');

  const delivered = await wf.executeActivity(
    activities.checkDelivery,
    { trackingId: shipment.trackingId }
  );

  return { orderId: order.id, status: 'completed' };
}

// Activities (actual work)
export async function processPayment(
  input: PaymentInput
): Promise<PaymentResult> {
  const stripe = new Stripe(process.env.STRIPE_KEY);
  const result = await stripe.charges.create({
    amount: input.amount,
    currency: 'usd',
  });
  return { success: result.paid, transactionId: result.id };
}
```

#### Inngest
- **Language**: Multi-language (Node.js, Python)
- **Architecture**: Serverless event/workflow platform
- **Pricing**:
  - Starter: $25/month (100K function runs/month)
  - Pro: $99/month (1M function runs/month)
  - Enterprise: Custom pricing
- **Throughput**: 1M+ events/month on starter plan
- **Latency**: 50-200ms
- **Best For**:
  - Serverless applications
  - Event-driven workflows
  - Scheduled functions
  - Webhook processing
  - SaaS platforms
- **Pros**:
  - No infrastructure management
  - Built-in queuing and retries
  - Excellent developer experience
  - Cost-effective for small-medium volume
  - Good free tier
- **Cons**:
  - Vendor lock-in
  - Limited customization
  - Throughput limits per plan
  - Smaller ecosystem
- **Scalability**: Automatic scaling per plan limit
- **Setup Time**: 1-2 hours
- **Example Cost**: 500K events/month = ~$50/mo

```typescript
// Example: Inngest setup
import { Inngest } from "inngest";

const inngest = new Inngest({ id: "my-app" });

export const sendWelcomeEmail = inngest.createFunction(
  { id: "send-welcome-email" },
  { event: "user.created" },
  async ({ event, step }) => {
    const emailSent = await step.run("send-email", async () => {
      return await sendEmail({
        to: event.data.email,
        template: "welcome",
      });
    });

    await step.sleep("wait-3-days", "3 days");

    await step.run("send-followup", async () => {
      return await sendEmail({
        to: event.data.email,
        template: "followup",
      });
    });

    return { success: true };
  }
);

// Trigger event
await inngest.send({
  name: "user.created",
  data: { userId: "user_123", email: "user@example.com" },
});
```

#### Trigger.dev
- **Language**: Node.js, Python
- **Architecture**: Managed workflow platform for serverless
- **Pricing**:
  - Starter: $10/month (100K task runs/month)
  - Pro: $50/month (1M task runs/month)
  - Enterprise: Custom
- **Throughput**: Similar to Inngest
- **Latency**: 100-300ms
- **Best For**:
  - Developer-friendly workflow automation
  - Integrations with external APIs
  - Background job management in serverless
  - Scheduled tasks
- **Pros**:
  - Excellent integrations (Slack, GitHub, etc.)
  - Good developer experience
  - Built-in test environment
  - Lower cost than Temporal
- **Cons**:
  - Newer platform (less maturity)
  - Limited to Node.js/Python
  - Smaller community
- **Scalability**: Automatic
- **Setup Time**: 1-2 hours
- **Example Cost**: 200K task runs/month = ~$20/mo

```typescript
// Example: Trigger.dev setup
import { TriggerClient, eventTrigger } from "@trigger.dev/sdk/v3";

const client = new TriggerClient({
  id: "my-app",
  apiKey: process.env.TRIGGER_API_KEY,
});

client.defineJob({
  id: "send-daily-digest",
  name: "Send Daily Digest",
  version: "0.0.1",
  trigger: eventTrigger({
    name: "daily.digest",
  }),
  run: async (payload, io, ctx) => {
    const recipients = await io.runTask(
      "get-recipients",
      async () => {
        return await getUsersWithDigest();
      }
    );

    for (const recipient of recipients) {
      await io.runTask(`send-${recipient.id}`, async () => {
        await sendEmail(recipient.email, generateDigest());
      });
    }

    return { sent: recipients.length };
  },
});

// Trigger event
await client.sendEvent({
  name: "daily.digest",
  payload: {},
});
```

---

## Message Brokers

Message brokers are designed for event streaming, pub/sub patterns, and decoupling of services.

### Message Broker Comparison Matrix

| Broker | Deployment | Throughput | Latency | Retention | Partitioning | Best For | Learning Curve |
|--------|-----------|-----------|---------|-----------|-------------|----------|----------------|
| **Apache Kafka** | Self-hosted / Cloud | 1M+/sec | <10ms | Days to years | Excellent | Event streaming, data pipelines | Steep |
| **Confluent Cloud** | Managed SaaS | 1M+/sec | <10ms | Days to years | Excellent | Enterprise event streaming | Steep |
| **RabbitMQ** | Self-hosted / Cloud | 50K/sec | <10ms | In-memory/disk | Limited | Traditional queuing, microservices | Moderate |
| **CloudAMQP** | Managed SaaS | 50K/sec | <10ms | In-memory/disk | Limited | RabbitMQ as a service | Moderate |
| **AWS SQS** | Managed SaaS | 3K/sec (standard) | <100ms | 15 min - 14 days | No | AWS ecosystem decoupling | Easy |
| **AWS SNS** | Managed SaaS | 100K+/sec | <100ms | No persistent | No | Pub/sub fanout | Easy |
| **AWS Kinesis** | Managed SaaS | 1M+/sec | <1s | 24h - 365 days | Excellent | Real-time streaming | Moderate |
| **Google Pub/Sub** | Managed SaaS | 1M+/sec | <100ms | 7 days default | No | Google ecosystem | Easy |
| **Redis Streams** | Self-hosted | 500K/sec | <1ms | In-memory | Limited | Simple pub/sub, caching | Easy |
| **Valkey** | Self-hosted | 500K/sec | <1ms | In-memory | Limited | Redis alternative | Easy |
| **NATS** | Self-hosted / Cloud | 500K+/sec | <10ms | Optional | No | Microservices, IoT | Easy |

### Apache Kafka

Kafka is the industry standard for high-throughput event streaming and data pipelines.

**Pricing**:
- Self-hosted: Infrastructure only ($500-5000+/mo for production cluster)
- Confluent Cloud: $0.10-0.35/hour per cluster + $0.10-1.00/GB ingested
  - Minimal cluster: $50-100/mo
  - Standard cluster: $500-2000/mo
  - Enterprise: Custom pricing

**Architecture**:
```
Producers → Topic (Partitions) → Consumer Groups
```

**Example Setup**:

```python
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json

# Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send events
future = producer.send('user-events', {
    'user_id': '12345',
    'action': 'login',
    'timestamp': '2026-03-02T10:00:00Z'
})

try:
    record_metadata = future.get(timeout=10)
    print(f"Sent to partition {record_metadata.partition}, offset {record_metadata.offset}")
except KafkaError as e:
    print(f"Failed to send: {e}")

# Consumer (single instance)
consumer = KafkaConsumer(
    'user-events',
    bootstrap_servers=['localhost:9092'],
    group_id='analytics-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'
)

for message in consumer:
    process_event(message.value)

# Consumer group scaling
# Run multiple instances, each gets assigned partitions automatically
```

**Throughput Benchmarks**:
- Single broker: 100K-500K events/sec
- 3-node cluster: 500K-2M events/sec
- 10-node cluster: 2M-10M events/sec

**When to use Kafka**:
- ✓ High-throughput event streaming (1M+/day)
- ✓ Event replay/history needed
- ✓ Complex stream processing (Apache Flink, Apache Spark)
- ✓ Data pipeline / ETL
- ✗ Simple task queuing (overkill)
- ✗ Low latency critical (<1ms)

### RabbitMQ

RabbitMQ uses the AMQP protocol and supports multiple queue types and routing patterns.

**Pricing**:
- Self-hosted: Infrastructure only (~$500-2000+/mo)
- CloudAMQP (Managed):
  - Little Lemur: $19/mo (4 GB RAM, 100 connections)
  - Tough Tiger: $49/mo (8 GB RAM, 500 connections)
  - Big Bunny: $99/mo (16 GB RAM, 2000 connections)

**Queue Types**:
- Classic Queue: Traditional queue
- Quorum Queue: Replicated, HA-enabled
- Stream Queue: Persistent log-like structure

**Example Setup**:

```python
import pika
import json

# Connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

# Declare queue with options
channel.queue_declare(
    queue='tasks',
    durable=True,  # Survives broker restart
    arguments={'x-message-ttl': 3600000}  # 1 hour TTL
)

# Producer
def publish_task(task_data):
    channel.basic_publish(
        exchange='',
        routing_key='tasks',
        body=json.dumps(task_data),
        properties=pika.BasicProperties(
            delivery_mode=2  # Persistent
        )
    )

# Consumer
def callback(ch, method, properties, body):
    task = json.loads(body)
    try:
        process_task(task)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

channel.basic_consume(queue='tasks', on_message_callback=callback)
channel.start_consuming()
```

**Routing Patterns**:
- Direct exchange: Task queues
- Topic exchange: Hierarchical routing (user.created, user.updated)
- Fanout exchange: Pub/sub broadcast
- Headers exchange: Header-based routing

**When to use RabbitMQ**:
- ✓ Traditional microservice queuing
- ✓ Complex routing patterns needed
- ✓ Moderate throughput (up to 100K/sec)
- ✓ AMQP protocol critical
- ✗ Very high throughput (>1M/sec)
- ✗ Event history/replay not needed

### AWS SQS (Simple Queue Service)

Managed queue service, pay-as-you-go, integrates with AWS ecosystem.

**Pricing**:
- Standard Queue: $0.40 per million requests ($0.000000004 per request)
- FIFO Queue: $0.50 per million requests
- Long-polling data transfer: Free
- Dead-letter queue: Same as standard queue
- CloudWatch monitoring: $0.10 per custom metric

**Example**: 100M requests/month = ~$40

**Characteristics**:
- Max throughput: 3,000 requests/second (standard)
- Max visibility timeout: 12 hours
- Max message size: 256 KB
- Max retention: 14 days
- At-least-once delivery (standard), exactly-once (FIFO)

**Example Setup**:

```python
import boto3
import json
from botocore.exceptions import ClientError

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789/my-queue'

# Producer
def send_message(task):
    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(task),
            MessageAttributes={
                'Priority': {
                    'StringValue': 'high',
                    'DataType': 'String'
                }
            },
            DelaySeconds=60  # Delay 60 seconds
        )
        print(f"Sent message {response['MessageId']}")
    except ClientError as e:
        print(f"Error: {e}")

# Consumer (batch processing)
def process_queue():
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20  # Long polling
        )

        if 'Messages' not in response:
            continue

        for message in response['Messages']:
            try:
                task = json.loads(message['Body'])
                process_task(task)

                # Delete after processing
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                print(f"Processing error: {e}")
                # Message will be redelivered after visibility timeout
```

**When to use SQS**:
- ✓ AWS-native applications
- ✓ Pay-as-you-go billing preferred
- ✓ Simple queuing (no complex routing)
- ✓ Moderate throughput (<1M/day)
- ✗ High throughput (>1M/day gets expensive)
- ✗ Complex routing patterns needed

### Redis Streams

Lightweight alternative to Kafka, using Redis data structure.

**Pricing**: Redis hosting $15-100+/mo depending on memory

**Characteristics**:
- Consumer groups with automatic acknowledgment
- Range queries by timestamp
- Throughput: 500K-1M events/sec
- Retention: In-memory only
- No persistence guarantee (unless Redis persistence enabled)

**Example Setup**:

```python
import redis
import json
import time

r = redis.Redis(host='localhost', port=6379)

# Producer
def publish_event(event):
    r.xadd('events', {'data': json.dumps(event)})

# Consumer group setup
r.xgroup_create('events', 'consumer-group', id='0', mkstream=True)

# Consumer
def consume_events(consumer_name):
    while True:
        # Read from pending messages first
        pending = r.xreadgroup('consumer-group', consumer_name,
                               {'events': '>'}, count=10)

        for stream, messages in pending:
            for message_id, data in messages:
                try:
                    event = json.loads(data[b'data'].decode())
                    process_event(event)
                    r.xack('events', 'consumer-group', message_id)
                except Exception as e:
                    print(f"Error: {e}")
```

**When to use Redis Streams**:
- ✓ Simple pub/sub with consumer groups
- ✓ Already using Redis for caching
- ✓ Lightweight alternative to Kafka
- ✗ Event history/long-term retention needed
- ✗ Multiple datacenters/replication critical

### NATS

High-performance messaging system, excellent for microservices.

**Pricing**:
- Self-hosted: Free (infrastructure cost)
- NATS Cloud: $0 - custom pricing (free tier available)

**Characteristics**:
- Ultra-low latency (<10ms)
- Multiple patterns: pub/sub, request/reply, queuing
- JetStream: Optional persistence layer
- Throughput: 500K+/sec
- Subjects-based routing (hierarchical)

**Example Setup**:

```python
import nats
import asyncio
import json

async def main():
    nc = await nats.connect("nats://localhost:4222")

    # Simple publish
    await nc.publish("user.created", b'{"user_id": "123"}')

    # Subscribe
    async def message_handler(msg):
        data = json.loads(msg.data.decode())
        print(f"Received: {data}")

    sub = await nc.subscribe("user.>", cb=message_handler)

    # Request/reply
    try:
        msg = await nc.request("service.query", b'{"id": 123}', timeout=1)
        print(f"Response: {msg.data}")
    except Exception as e:
        print(f"No response: {e}")

    # Cleanup
    await nc.close()

asyncio.run(main())
```

**When to use NATS**:
- ✓ Microservice communication
- ✓ Low-latency critical
- ✓ Request/reply patterns needed
- ✓ Lightweight/minimal overhead
- ✗ Event history/replay needed
- ✗ Complex stream processing

---

## Event-Driven Patterns

### Outbox Pattern

The Outbox Pattern ensures reliable event publishing by storing events in the same transaction as business logic.

**Problem**: Dual write problem - publishing to message broker while saving to database can fail halfway through.

**Solution**: Write events to local outbox table, then separate process publishes from outbox to broker.

**Architecture**:

```
┌─────────────────────┐
│   Business Logic    │
│   (Order Service)   │
└──────────┬──────────┘
           │
           │ Same transaction
           ↓
    ┌─────────────────┐         ┌─────────────────┐
    │  Orders Table   │         │  Outbox Table   │
    │  ────────────   │         │  ─────────────  │
    │ order_id: 1001  │         │ event_type: ... │
    │ status: PENDING │         │ payload: ...    │
    │ created_at: ... │         │ published: false│
    └─────────────────┘         └────────┬────────┘
                                         │
                                    Poll/Subscribe
                                         │
                                         ↓
                    ┌─────────────────────────────────┐
                    │  Outbox Publisher Service       │
                    │  (polls every 1-5 seconds)      │
                    └─────────────────┬───────────────┘
                                      │
                                      ↓
                          ┌─────────────────────┐
                          │  Message Broker     │
                          │  (Kafka/RabbitMQ)   │
                          └─────────────────────┘
```

**Implementation**:

```python
from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import json
from datetime import datetime

Base = declarative_base()

class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(String, primary_key=True)
    aggregate_id = Column(String)  # e.g., order_id
    event_type = Column(String)
    payload = Column(String)  # JSON
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

def create_order_with_event(session: Session, order_data: dict):
    """Create order and outbox event in single transaction"""
    order = Order(**order_data)
    session.add(order)

    # Add outbox event
    event = OutboxEvent(
        id=f"order-created-{uuid4()}",
        aggregate_id=order.id,
        event_type="OrderCreated",
        payload=json.dumps({
            "order_id": order.id,
            "customer_id": order.customer_id,
            "total": str(order.total),
            "created_at": order.created_at.isoformat()
        })
    )
    session.add(event)

    session.commit()  # Atomic!
    return order

# Separate service: Outbox Publisher
def publish_outbox_events(session: Session, broker):
    """Periodically publish unpublished events"""
    unpublished = session.query(OutboxEvent)\
        .filter(OutboxEvent.published == False)\
        .order_by(OutboxEvent.created_at)\
        .all()

    for event in unpublished:
        try:
            broker.publish(
                topic=event.event_type,
                message=event.payload
            )
            event.published = True
            event.published_at = datetime.utcnow()
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Failed to publish {event.id}: {e}")
            # Will retry next cycle
```

**Benefits**:
- ✓ Guaranteed event delivery
- ✓ Exactly-once semantics (with idempotent consumers)
- ✓ No complex distributed transactions
- ✓ Easy to implement with relational databases

**Considerations**:
- Requires polling or change data capture (CDC) for publisher
- Introduces slight delay in event availability
- Requires cleanup job for old published events

**When to use Outbox Pattern**:
- ✓ Critical event delivery required
- ✓ Using relational database
- ✓ Can tolerate slight latency
- ✓ E-commerce, financial transactions
- ✗ Real-time streaming (millisecond latency)
- ✗ Document databases without transactions

---

### Saga Pattern

Saga Pattern manages distributed transactions across multiple services using either choreography or orchestration.

**Problem**: ACID transactions don't work across service boundaries.

**Solution**: Break distributed transaction into local transactions coordinated by saga.

#### Choreography Saga

Each service listens to events and triggers next step.

**Architecture**:

```
Order Service          Payment Service       Inventory Service
    │                        │                      │
    │─ OrderCreated event ──>│                      │
    │                        │─ PaymentProcessed ──>│
    │                        │      event           │
    │                        │                      │
    │<── PaymentFailed ─────────────────────────────│
    │     event (if needed)
    │
    └─ OrderCancelled ───────────────────────────────>
       (compensating transaction)
```

**Implementation**:

```python
# Order Service
class OrderService:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.event_bus.subscribe("PaymentProcessed", self.on_payment_processed)
        self.event_bus.subscribe("PaymentFailed", self.on_payment_failed)
        self.event_bus.subscribe("InventoryReserved", self.on_inventory_reserved)
        self.event_bus.subscribe("InventoryReservationFailed", self.on_inventory_failed)

    def create_order(self, order_data):
        order = Order(**order_data)
        order.status = "PENDING_PAYMENT"
        db.session.add(order)
        db.session.commit()

        # Trigger next step
        self.event_bus.publish("OrderCreated", {
            "order_id": order.id,
            "customer_id": order.customer_id,
            "amount": order.total
        })
        return order

    def on_payment_processed(self, event):
        order = Order.find(event["order_id"])
        order.status = "PENDING_INVENTORY"
        db.session.commit()

        self.event_bus.publish("ReserveInventory", {
            "order_id": order.id,
            "items": order.items
        })

    def on_inventory_reserved(self, event):
        order = Order.find(event["order_id"])
        order.status = "CONFIRMED"
        db.session.commit()

    def on_payment_failed(self, event):
        order = Order.find(event["order_id"])
        order.status = "CANCELLED"
        db.session.commit()
        # No need to reverse - inventory was never reserved

# Payment Service
class PaymentService:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.event_bus.subscribe("OrderCreated", self.on_order_created)

    def on_order_created(self, event):
        try:
            result = stripe.charge.create(
                amount=event["amount"],
                customer_id=event["customer_id"]
            )
            self.event_bus.publish("PaymentProcessed", {
                "order_id": event["order_id"],
                "transaction_id": result.id
            })
        except StripeError as e:
            self.event_bus.publish("PaymentFailed", {
                "order_id": event["order_id"],
                "reason": str(e)
            })

# Inventory Service
class InventoryService:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.event_bus.subscribe("ReserveInventory", self.on_reserve_inventory)

    def on_reserve_inventory(self, event):
        try:
            reservation = Inventory.reserve_items(event["items"])
            self.event_bus.publish("InventoryReserved", {
                "order_id": event["order_id"],
                "reservation_id": reservation.id
            })
        except InsufficientInventoryError:
            self.event_bus.publish("InventoryReservationFailed", {
                "order_id": event["order_id"],
                "reason": "Out of stock"
            })
            # Trigger compensating transaction
            self.event_bus.publish("CancelOrder", {
                "order_id": event["order_id"]
            })
```

**Pros**:
- Simple, distributed
- Loose coupling
- Each service owns compensation logic

**Cons**:
- Hard to follow flow
- Difficult to debug
- Risk of circular dependencies
- No central visibility

---

#### Orchestration Saga

Central orchestrator directs each step.

**Architecture**:

```
┌──────────────────────────────┐
│   Order Saga Orchestrator    │
│  (Temporal/Durable Logic)    │
└──────────┬───────────────────┘
           │
      Step 1: Process Payment
           │
      ┌────▼──────────────────┐
      │  Payment Service      │
      └──────────────────────┘
           │
      Step 2: Reserve Inventory
           │
      ┌────▼──────────────────┐
      │  Inventory Service    │
      └──────────────────────┘
           │
      Step 3: Create Shipment
           │
      ┌────▼──────────────────┐
      │  Shipment Service     │
      └──────────────────────┘
```

**Implementation with Temporal**:

```typescript
import * as workflow from '@temporalio/workflow';
import * as activities from './activities';

export interface OrderInput {
  orderId: string;
  customerId: string;
  items: OrderItem[];
  amount: number;
}

export async function orderSaga(input: OrderInput) {
  const results = {
    payment: null,
    inventory: null,
    shipment: null,
  };

  try {
    // Step 1: Process payment
    results.payment = await workflow.executeActivity(
      activities.processPayment,
      { customerId: input.customerId, amount: input.amount },
      { startToCloseTimeout: '10 minutes', retry: { maxAttempts: 3 } }
    );

    // Step 2: Reserve inventory
    results.inventory = await workflow.executeActivity(
      activities.reserveInventory,
      { items: input.items },
      { startToCloseTimeout: '5 minutes', retry: { maxAttempts: 3 } }
    );

    // Step 3: Create shipment
    results.shipment = await workflow.executeActivity(
      activities.createShipment,
      { orderId: input.orderId },
      { startToCloseTimeout: '10 minutes', retry: { maxAttempts: 3 } }
    );

    return { success: true, results };

  } catch (error) {
    // Compensating transactions on failure
    if (results.payment) {
      await workflow.executeActivity(activities.refundPayment, {
        transactionId: results.payment.transactionId,
      });
    }

    if (results.inventory) {
      await workflow.executeActivity(activities.releaseInventory, {
        reservationId: results.inventory.reservationId,
      });
    }

    throw error;
  }
}
```

**Pros**:
- Clear flow
- Easy to debug and test
- Central visibility
- Handles long-running processes

**Cons**:
- Orchestrator becomes central point of failure
- More complex to implement
- Tight coupling to orchestrator

**When to use Saga Pattern**:
- ✓ Distributed transactions needed
- ✓ Cross-service workflows
- ✓ Long-running processes (order processing)
- ✓ Error recovery/compensation needed
- ✗ ACID transactions available in single database
- ✗ Simple service-to-service calls

---

### CQRS (Command Query Responsibility Segregation)

Separate read and write models.

**Architecture**:

```
                    User Request
                         │
         ┌───────────────┴───────────────┐
         │                               │
    Command                          Query
   (Write Model)                   (Read Model)
         │                               │
         ▼                               ▼
  ┌────────────────┐            ┌────────────────┐
  │  Master DB     │            │  Read Cache    │
  │ (Normalized)   │            │  (Denormalized)│
  │  ┌──────────┐  │            │  ┌──────────┐  │
  │  │ Orders   │  │            │  │ OrderView│  │
  │  │ Items    │  │            │  │ (with    │  │
  │  │ Customers│  │            │  │  joins)  │  │
  │  └──────────┘  │            │  └──────────┘  │
  └────────┬───────┘            └──────────────┘
           │
           │ Events
           │
      ┌────▼──────────┐
      │ Event Stream  │
      │  (Kafka, etc) │
      └────┬──────────┘
           │
           │ Sync
           │
      ┌────▼──────────────┐
      │ Read Model Builder│
      │ (Event Handler)   │
      └───────────────────┘
```

**Implementation**:

```python
from dataclasses import dataclass
from typing import List

# Write Model (Commands)
@dataclass
class CreateOrderCommand:
    customer_id: str
    items: List[dict]

    def validate(self):
        if not self.customer_id:
            raise ValueError("customer_id required")
        if not self.items:
            raise ValueError("items required")

class OrderCommandHandler:
    def handle_create_order(self, cmd: CreateOrderCommand):
        cmd.validate()

        order = Order(
            customer_id=cmd.customer_id,
            items=cmd.items,
            status="PENDING"
        )
        db.session.add(order)
        db.session.commit()

        # Publish event for read model
        event_bus.publish("OrderCreated", {
            "order_id": order.id,
            "customer_id": order.customer_id,
            "items": order.items
        })

        return order.id

# Read Model (Queries)
class OrderReadModel:
    """Denormalized view optimized for queries"""

    def get_customer_orders(self, customer_id: str):
        # Fast query - no joins needed
        return redis.get(f"customer:{customer_id}:orders")

    def search_orders(self, filters: dict):
        # Elasticsearch for complex queries
        return es.search(index="orders", query=filters)

class OrderReadModelBuilder:
    def on_order_created(self, event):
        """Update read model when OrderCreated event received"""
        order_view = {
            "order_id": event["order_id"],
            "customer_id": event["customer_id"],
            "items": event["items"],
            "created_at": datetime.utcnow().isoformat(),
            "status": "PENDING"
        }

        # Update cache
        redis.lpush(f"customer:{event['customer_id']}:orders",
                   json.dumps(order_view))

        # Update search index
        es.index(index="orders", document=order_view)
```

**Benefits**:
- ✓ Queries optimized independently
- ✓ Can scale reads and writes separately
- ✓ Multiple read models for different use cases
- ✓ Event sourcing friendly

**Drawbacks**:
- ✓ Eventually consistent
- ✓ More complexity
- ✓ Requires strong operational discipline

**When to use CQRS**:
- ✓ Read/write ratio very different (100:1 reads)
- ✓ Complex read queries needed
- ✓ Multiple clients with different query needs
- ✓ Real-time dashboards
- ✗ Simple CRUD applications
- ✗ Strong consistency critical everywhere

---

### Event Sourcing

Store all state changes as immutable events instead of current state.

**Advantages**:
- Complete audit trail
- Temporal queries ("state as of date X")
- Event replay for debugging
- Natural fit with event-driven systems
- Optimistic locking (events are append-only)

**Disadvantages**:
- Learning curve
- Event schema evolution challenges
- Storage requirements
- Eventual consistency
- Complex testing

**Implementation**:

```python
from datetime import datetime
import json

class EventStore:
    """Immutable event log"""

    def append(self, aggregate_id: str, event_type: str, payload: dict):
        event = {
            "aggregate_id": aggregate_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "version": self.get_next_version(aggregate_id)
        }
        db.events.insert_one(event)
        return event

    def get_events(self, aggregate_id: str, from_version: int = 0):
        return list(db.events.find({
            "aggregate_id": aggregate_id,
            "version": {"$gt": from_version}
        }).sort("version", 1))

class Order:
    """Aggregate root - rebuilt from events"""

    def __init__(self, aggregate_id: str, event_store: EventStore):
        self.id = aggregate_id
        self.items = []
        self.status = "INITIAL"
        self.total = 0
        self.version = 0
        self.event_store = event_store
        self._changes = []

        # Rebuild from events
        self._load_from_history()

    def _load_from_history(self):
        events = self.event_store.get_events(self.id)
        for event in events:
            self._apply_event(event)

    def _apply_event(self, event: dict):
        """Apply event to current state"""
        if event["event_type"] == "OrderCreated":
            self.status = "CREATED"
            self.items = event["payload"]["items"]

        elif event["event_type"] == "ItemAdded":
            self.items.append(event["payload"]["item"])

        elif event["event_type"] == "OrderConfirmed":
            self.status = "CONFIRMED"
            self.total = event["payload"]["total"]

        self.version = event.get("version", self.version)

    def create_order(self, items: List[dict]):
        event = {
            "event_type": "OrderCreated",
            "payload": {"items": items}
        }
        self._record_change(event)
        self._apply_event(event)

    def confirm_order(self, total: float):
        event = {
            "event_type": "OrderConfirmed",
            "payload": {"total": total}
        }
        self._record_change(event)
        self._apply_event(event)

    def _record_change(self, event: dict):
        self._changes.append(event)

    def save(self):
        for event in self._changes:
            self.event_store.append(self.id, event["event_type"], event["payload"])
        self._changes = []
```

**When to use Event Sourcing**:
- ✓ Audit/compliance critical
- ✓ Temporal queries ("state as of date X")
- ✓ Complex domain logic
- ✓ Microservices with event-driven architecture
- ✗ Simple CRUD applications
- ✗ Strong consistency critical

---

## Decision Matrices

### Queue System Selection Matrix

**By Language**:

| Language | Best Choice | Alternative | Last Resort |
|----------|------------|-------------|------------|
| **Node.js/TypeScript** | BullMQ | Inngest | AWS Lambda |
| **Python** | Celery | APScheduler | RQ |
| **Ruby/Rails** | Sidekiq Pro | Resque | DelayedJob |
| **Java** | Spring Boot Task | Temporal | AWS SQS |
| **Go** | Temporal | NATS | Custom |
| **Multi-language** | Temporal Cloud | Kafka | AWS SQS |

**By Scale (daily events)**:

```
Events/Day    | Recommended              | Infrastructure        | Cost/month
──────────────┼──────────────────────────┼───────────────────────┼────────────
<100K         | Lightweight queue        | Single Redis instance | $20-50
              | (BullMQ, RQ)             |                       |
──────────────┼──────────────────────────┼───────────────────────┼────────────
100K-1M       | Self-hosted Redis queue  | Redis cluster, 1-2    | $50-200
              | or simple broker         | app servers           |
──────────────┼──────────────────────────┼───────────────────────┼────────────
1M-10M        | Managed service          | Inngest, Trigger.dev, | $100-500
              | or RabbitMQ/Kafka        | or self-hosted Kafka  |
──────────────┼──────────────────────────┼───────────────────────┼────────────
10M-100M      | Kafka or Temporal Cloud  | Confluent or Temporal | $500-3000
──────────────┼──────────────────────────┼───────────────────────┼────────────
100M+         | Enterprise Kafka         | Multi-cluster Kafka   | $3000+
              | or Temporal Enterprise   | setup                 |
```

**By Requirements**:

| Requirement | Recommendation |
|-------------|-----------------|
| **Exactly-once semantics** | Temporal, Outbox pattern |
| **Long-running workflows** | Temporal, Durable Functions |
| **Event replay/debugging** | Event sourcing + Kafka |
| **Simple task queue** | BullMQ, Sidekiq |
| **Data pipeline/ETL** | Kafka, Celery |
| **Serverless/Functions** | Inngest, Trigger.dev, AWS Lambda |
| **Microservice orchestration** | Temporal, Saga pattern |
| **Low latency critical** | NATS, Redis Streams |
| **Minimal infrastructure** | Managed service (Inngest, Trigger.dev) |
| **Distributed transactions** | Saga + event broker |

**By Budget**:

```
Budget        | Recommendation
──────────────┼────────────────────────────────────────
Free          | BullMQ, Celery, RQ, RabbitMQ (self-host)
$10-50/mo     | Trigger.dev, Redis managed
$50-200/mo    | Inngest, Sidekiq Pro, RabbitMQ managed
$500+/mo      | Temporal Cloud, Confluent Cloud
Enterprise    | Kafka Enterprise, Temporal Enterprise
```

---

### Self-Hosted vs Managed Comparison

| Factor | Self-Hosted | Managed |
|--------|-----------|---------|
| **Initial Cost** | Low ($0) | Medium-High ($25-100/mo) |
| **Operational Overhead** | High (24/7 monitoring, updates, backups) | Low (provider handles) |
| **Scaling Complexity** | High (provision nodes, balancing) | Low (automatic) |
| **Customization** | Excellent | Limited |
| **Performance Tuning** | Full control | Limited control |
| **Security** | Self-responsible | Provider-managed |
| **SLA/Support** | Self-provided | Guaranteed SLA |
| **Data Residency** | Full control | May be limited |
| **Break-even** | ~50K events/day | ~500K events/day |
| **Best For** | Mature teams, cost-sensitive, high volume | Startups, limited ops budget |

**Economics Breakdown**:

Self-hosted Kafka (3-node cluster):
```
Infrastructure:     $2000-5000/month
Operations:         1 FTE (~$150K/year = $12.5K/month)
Total:             $14-17K+/month
Break-even:        ~50M events/day
```

Confluent Cloud (standard cluster):
```
Cluster cost:      $500-2000/month
Data ingestion:    $0.10-1.00/GB
(100M events @ 1KB = 100GB = $100-1000)
Total:             $600-3000/month
```

Self-hosted RabbitMQ (single instance):
```
Infrastructure:    $50-200/month
Operations:        0.2 FTE (~$2500/month)
Total:             $2700/month
Break-even:        ~30M messages/day
```

Inngest/Trigger.dev:
```
Starter:          $25/month
Pro:              $99/month
Enterprise:       Custom (thousands)
Break-even:       ~100M events/month then switch to enterprise
```

---

### Sync vs Async Processing Decision Tree

```
                    Must respond
                    immediately?
                         │
                    ┌────┴────┐
                    │         │
                   YES       NO
                    │         │
                    ▼         ▼
               SYNC-ISH    ASYNC
                    │         │
            Timeout 1-10s  Queue/Schedule
            in request     │
                    │      ├─ Fire and forget
                    │      ├─ Delayed execution
            Return 202     ├─ Background worker
            Accepted       └─ Event stream
                    │
                    ▼
         Large/complex task?
                    │
            ┌───────┴────────┐
           YES              NO
            │                │
            ▼                ▼
        Async job    Return result
        (BullMQ,    in response
        Celery)
```

---

## Real-World Architectures

### E-Commerce Order Processing Pipeline

**Requirements**:
- Process orders reliably
- Handle payment, inventory, shipping coordination
- Long-running workflow (delivery takes days)
- Compensate on failures
- Audit trail required

**Architecture**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway / Web Server                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ POST /orders
                         ▼
            ┌────────────────────────────┐
            │     Order Service          │
            │   (Command Handler)        │
            └────────────┬───────────────┘
                         │
                    Store order
                    Create event
                         │
            ┌────────────▼────────────────┐
            │   Events (Outbox Table)     │
            │  ────────────────────────   │
            │  order_created              │
            │  payment_processed          │
            │  inventory_reserved         │
            │  shipment_created           │
            └────────────┬────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐   ┌──────────┐  ┌──────────────┐
    │  Kafka  │   │ Event    │  │ Saga         │
    │ Topics  │   │ Publisher│  │ Orchestrator │
    │         │   │ Service  │  │ (Temporal)   │
    │ order   │   │          │  │              │
    │ payment │   │ (Polls   │  │ Coordinates: │
    │ ship    │   │  every   │  │ 1. Payment   │
    └─────────┘   │  5 sec)  │  │ 2. Inventory │
         │        │          │  │ 3. Shipment  │
         │        └──────────┘  │ 4. Notify    │
         │                      └──────┬───────┘
         │                            │
    ┌────┴────────────────────────────┴──────────────────┐
    │                                                     │
    ▼                                                     ▼
Payment Service                             Inventory Service
├─ Stripe API                              ├─ Reserve items
├─ Retry failed payments                  ├─ Release on cancel
└─ Emit PaymentProcessed/Failed           └─ Emit InventoryReserved/Failed
    │                                          │
    └────────────────────┬─────────────────────┘
                         │
                         ▼
            Shipping Service
            ├─ Create shipment
            ├─ Track delivery
            └─ Emit ShipmentCreated/Delivered

    ┌────────────────────────────────────────┐
    │  Read Models (Projections)             │
    │ ────────────────────────────────────── │
    │  ├─ OrderView (for customer)           │
    │  ├─ InventoryView (for inventory team) │
    │  └─ RevenueView (for finance)          │
    │                                        │
    │  Updated via Kafka events              │
    │  Stored in Redis / MongoDB             │
    └────────────────────────────────────────┘

    ┌────────────────────────────────────────┐
    │  Notifications                         │
    │ ────────────────────────────────────── │
    │  ├─ Email (via SendGrid)               │
    │  ├─ SMS (via Twilio)                   │
    │  └─ In-app (Push to WebSocket)         │
    │                                        │
    │  Triggered by events                   │
    │  Processed by notification workers     │
    └────────────────────────────────────────┘
```

**Technology Stack**:

```
Queue/Orchestration:    Temporal Cloud ($100-300/mo for 10M actions)
Message Broker:         Kafka / Confluent Cloud ($500-1000/mo)
Outbox Storage:         PostgreSQL (existing)
Read Models:            Redis ($30-100/mo) + PostgreSQL
Notification Queue:     BullMQ (Redis)
Monitoring:             Datadog / New Relic ($100-500/mo)

Total Monthly Cost: $1000-2000
```

**Workflow Code (Temporal)**:

```typescript
export async function orderProcessingWorkflow(order: Order) {
  const logger = workflow.createLogger();

  try {
    logger.info('Starting order workflow', { orderId: order.id });

    // Step 1: Process payment (with retry)
    const payment = await workflow.executeActivity(
      activities.processPayment,
      {
        customerId: order.customerId,
        amount: order.total,
      },
      {
        startToCloseTimeout: '10 minutes',
        retry: {
          initialInterval: '5 seconds',
          maxInterval: '1 minute',
          maxAttempts: 3,
        },
      }
    );

    // Step 2: Reserve inventory (compensate if fails)
    const inventory = await workflow.executeActivity(
      activities.reserveInventory,
      {
        items: order.items,
      },
      {
        startToCloseTimeout: '5 minutes',
        retry: { maxAttempts: 2 },
      }
    ).catch(async (error) => {
      // Compensating transaction
      await workflow.executeActivity(activities.refundPayment, {
        transactionId: payment.transactionId,
      });
      throw error;
    });

    // Step 3: Create shipment
    const shipment = await workflow.executeActivity(
      activities.createShipment,
      {
        orderId: order.id,
        address: order.shippingAddress,
      },
      {
        startToCloseTimeout: '10 minutes',
        retry: { maxAttempts: 3 },
      }
    ).catch(async (error) => {
      // Compensating transactions
      await workflow.executeActivity(activities.releaseInventory, {
        reservationId: inventory.reservationId,
      });
      await workflow.executeActivity(activities.refundPayment, {
        transactionId: payment.transactionId,
      });
      throw error;
    });

    // Step 4: Wait for delivery (long timeout)
    await workflow.sleep('14 days');
    const delivered = await workflow.executeActivity(
      activities.checkDelivery,
      {
        trackingId: shipment.trackingId,
      }
    );

    // Step 5: Send confirmation
    await workflow.executeActivity(activities.sendDeliveryEmail, {
      orderId: order.id,
      customerId: order.customerId,
    });

    logger.info('Order workflow completed', { orderId: order.id });
    return { orderId: order.id, status: 'COMPLETED' };

  } catch (error) {
    logger.error('Order workflow failed', { orderId: order.id, error });
    await workflow.executeActivity(activities.notifyAdmins, {
      orderId: order.id,
      error: error.message,
    });
    throw error;
  }
}
```

---

### Notification System Architecture

**Requirements**:
- Send millions of notifications daily
- Multiple channels (email, SMS, push, in-app)
- Deduplication
- Rate limiting per user
- High throughput
- Monitoring

**Architecture**:

```
┌──────────────────────────────────────────┐
│      Event Sources                       │
│  ├─ Order Service (OrderShipped)         │
│  ├─ User Service (FollowUserRequest)     │
│  └─ System (DailyDigest)                 │
└────────────┬─────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────┐
│   Kafka Topic: notifications             │
│   Partitioned by user_id (1000 parts)    │
│   Throughput: 100K events/sec            │
└────────────┬─────────────────────────────┘
             │
      ┌──────┴──────────────────┬────────────────┐
      │                         │                │
      ▼                         ▼                ▼
┌──────────────┐      ┌──────────────┐   ┌──────────────┐
│Email         │      │SMS           │   │Push          │
│Processor     │      │Processor     │   │Processor     │
│(100 workers) │      │(50 workers)  │   │(100 workers) │
└──────┬───────┘      └──────┬───────┘   └──────┬───────┘
       │                     │                  │
       │ Deduplication, Rate Limiting
       │ (Redis)
       │
    ┌──┴───────────────────┬──────────────┬──────────┐
    │                      │              │          │
    ▼                      ▼              ▼          ▼
SendGrid          Twilio         Firebase      In-App
(Email)           (SMS)          Cloud         WebSocket
                                 Messaging     Queue


Metrics & Monitoring:
├─ Kafka lag per consumer group
├─ Send success rate per provider
├─ Delivery time (p50, p99)
├─ Error rates and types
└─ Consumer processing time
```

**Implementation**:

```python
# Celery configuration
from celery import Celery, group
from kafka import KafkaConsumer
import json

app = Celery('notifications', broker='redis://localhost:6379')

# Kafka consumer for notifications
consumer = KafkaConsumer(
    'notifications',
    bootstrap_servers=['localhost:9092'],
    group_id='notification-processors',
    max_poll_records=1000
)

class NotificationProcessor:
    @app.task(bind=True, max_retries=3, rate_limit='100/m')
    def send_email(self, notification: dict):
        """Send email notification with deduplication"""
        user_id = notification['user_id']
        notification_type = notification['type']

        # Check deduplication cache
        cache_key = f"notif:{user_id}:{notification_type}"
        if redis.exists(cache_key):
            return {'status': 'deduplicated', 'id': notification['id']}

        # Rate limiting
        rate_key = f"rate:{user_id}:email"
        if not self.check_rate_limit(rate_key, limit=5, window=3600):
            # Schedule for later
            return self.retry(countdown=300)

        try:
            # Compose email
            email_data = self.compose_email(notification)

            # Send via SendGrid
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(email_data)

            # Mark as sent in cache
            redis.setex(cache_key, 86400, notification['id'])

            return {
                'status': 'sent',
                'id': notification['id'],
                'message_id': response.headers['X-Message-ID']
            }

        except SendGridAPIError as e:
            self.send_task('log_error', args=[notification['id'], str(e)])
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    @staticmethod
    def check_rate_limit(key: str, limit: int, window: int) -> bool:
        """Token bucket rate limiting"""
        current = redis.incr(key)
        if current == 1:
            redis.expire(key, window)
        return current <= limit

    @staticmethod
    def compose_email(notification: dict) -> Email:
        """Compose email based on notification type"""
        templates = {
            'order_shipped': 'order-shipped.html',
            'user_followed': 'user-followed.html',
            'daily_digest': 'daily-digest.html'
        }

        template_name = templates.get(notification['type'], 'generic.html')

        return Email(
            from_email='noreply@example.com',
            to_emails=notification['recipient'],
            subject=notification['subject'],
            html_content=render_template(
                template_name,
                data=notification['data']
            )
        )

# Worker process
def notification_worker():
    for message in consumer:
        notification = json.loads(message.value)

        # Route to appropriate processor
        if notification['channel'] == 'email':
            NotificationProcessor.send_email.delay(notification)
        elif notification['channel'] == 'sms':
            NotificationProcessor.send_sms.delay(notification)
        elif notification['channel'] == 'push':
            NotificationProcessor.send_push.delay(notification)

if __name__ == '__main__':
    notification_worker()
```

**Scaling Metrics**:

```
At 10M notifications/day:
├─ Kafka partitions: 1000 (1000 * 10K/sec)
├─ Email workers: 100 (100K/sec throughput)
├─ SMS workers: 50 (50K/sec throughput)
├─ Push workers: 100
├─ Redis instances: 2 (dedup + rate limiting)
└─ SendGrid quota: 500K/day ($50-100/mo)

Cost Breakdown:
├─ Kafka (Confluent): $1000/mo
├─ Redis: $200/mo
├─ Compute (workers): $500/mo
├─ Monitoring: $200/mo
├─ Email provider (SendGrid): $100/mo
└─ Total: ~$2000/mo
```

---

## Performance Benchmarks

### Throughput Benchmarks (events/second)

```
System              | Single-Node | Cluster (10x) | Notes
────────────────────┼─────────────┼───────────────┼──────────────────────
BullMQ              | 10K         | 100K          | Redis-backed
Celery              | 50K         | 500K          | Depends on broker
Sidekiq             | 10K         | 100K          | Ruby/Redis
RQ                  | 1K          | 10K           | Simple, slow
Kafka               | 500K        | 5M            | Industry std
RabbitMQ            | 50K         | 500K          | AMQP protocol
Redis Streams       | 500K        | N/A (single) | In-memory
AWS SQS             | 3K          | Limited 100K  | Service limits
Temporal            | 100K        | 1M            | Durable workflows
Google Pub/Sub      | 100K        | 1M+           | Managed service
NATS                | 500K        | 5M+           | Ultra-high throughput
```

### Latency Benchmarks (p99 milliseconds)

```
System              | Min         | Typical       | Max
────────────────────┼─────────────┼───────────────┼──────────────
BullMQ              | 10ms        | 50ms          | 200ms
Celery              | 20ms        | 100ms         | 500ms
Kafka               | 1ms         | 10ms          | 50ms
RabbitMQ            | 5ms         | 20ms          | 100ms
Redis Streams       | <1ms        | 5ms           | 20ms
AWS SQS             | 50ms        | 100ms         | 500ms
Temporal            | 100ms       | 500ms         | 2000ms (includes durable)
Google Pub/Sub      | 50ms        | 150ms         | 500ms
NATS                | 1ms         | 5ms           | 20ms
```

### Memory Usage Per Event

```
System              | Per Event   | 1M Events     | Notes
────────────────────┼─────────────┼───────────────┼──────────────
Redis (in memory)   | 500 bytes   | 500 MB        | With metadata
Kafka (disk)        | 300 bytes   | 300 MB        | Compressed
RabbitMQ (RAM)      | 600 bytes   | 600 MB        | With headers
Temporal (disk)     | 1 KB        | 1 GB          | Includes replay data
```

---

## Cost Analysis

### Total Cost of Ownership (TCO) Comparison

**Scenario: 10M events/month, 3-person DevOps team**

#### Option 1: BullMQ + Self-Hosted Redis

```
Infrastructure:
├─ Redis (AWS ElastiCache t3.medium): $50/mo
├─ EC2 workers (2x t3.small): $20/mo
└─ Subtotal: $70/mo

Operations:
├─ Monitoring: $50/mo (CloudWatch)
├─ Team cost (0.1 FTE): $12,500/year = $1,042/mo
└─ Subtotal: $1,092/mo

Total Monthly: ~$1,162/mo
Annual: ~$13,944

Advantages:
- Low cost
- Full control
- Good for Node.js teams

Disadvantages:
- Ops overhead (backups, updates, scaling)
- Single point of failure
- Limited to ~100K events/sec
```

#### Option 2: Temporal Cloud

```
Infrastructure:
├─ Temporal Cloud (minimum): $100/mo
├─ Estimated 10M actions: +$1000/mo
└─ Total: $1,100/mo

Operations:
├─ Monitoring: $50/mo (included + Datadog)
├─ Team cost (0.01 FTE): $1,250/year = $104/mo
└─ Subtotal: $154/mo

Total Monthly: ~$1,254/mo
Annual: ~$15,048

Advantages:
- Reliable, battle-tested
- Multi-language support
- Perfect for long-running workflows
- Minimal operations

Disadvantages:
- Higher monthly cost
- Vendor lock-in
- Not ideal for simple tasks
```

#### Option 3: Inngest

```
Infrastructure:
├─ Inngest Pro: $99/mo (1M function runs)
├─ 10M events likely = $200-300/mo estimated
└─ Total: ~$300/mo

Operations:
├─ Monitoring: $0 (included)
├─ Team cost (0.01 FTE): $1,250/year = $104/mo
└─ Subtotal: $104/mo

Total Monthly: ~$404/mo
Annual: ~$4,848

Advantages:
- Lowest total cost
- Serverless, zero ops
- Great for startups

Disadvantages:
- Limited to their platform
- Feature constraints
- May outgrow quickly
```

#### Option 4: Confluent Cloud + RabbitMQ

```
Infrastructure:
├─ Confluent Cloud cluster: $1,000/mo
├─ RabbitMQ (CloudAMQP): $200/mo
├─ EC2 processor workers: $100/mo
└─ Subtotal: $1,300/mo

Operations:
├─ Monitoring: $200/mo
├─ Team cost (0.2 FTE): $25,000/year = $2,083/mo
└─ Subtotal: $2,283/mo

Total Monthly: ~$3,583/mo
Annual: ~$43,000

Advantages:
- Enterprise-grade
- Multi-datacenter capable
- Excellent throughput

Disadvantages:
- Expensive for moderate load
- Overkill for <100M events/day
- Requires specialized expertise
```

---

### Cost per Million Events

```
System              | Compute       | Storage  | Total/M Events
────────────────────┼───────────────┼──────────┼─────────────────
BullMQ (self-host)  | $0.10         | Free     | $0.10
Celery (self-host)  | $0.10         | $0.05    | $0.15
Inngest             | $0.25         | $0.05    | $0.30
Trigger.dev         | $0.20         | $0.05    | $0.25
Temporal Cloud      | $0.10         | $0.10    | $0.20
AWS Lambda          | $0.20         | N/A      | $0.20
AWS SQS             | $0.40         | N/A      | $0.40
Kafka (self-host)   | $0.05         | $0.10    | $0.15
Confluent Cloud     | $0.10         | $1.00    | $1.10
Google Pub/Sub      | $0.20         | N/A      | $0.20
```

---

## Implementation Considerations

### Fault Tolerance Strategies

**Retry Strategies**:

```python
# Exponential backoff with jitter
import random
import math

def calculate_backoff(attempt: int, base: int = 2, max_wait: int = 3600):
    """Exponential backoff with jitter"""
    exponential = min(max_wait, base ** attempt)
    jitter = random.uniform(0, exponential)
    return jitter

# Example: Celery task with exponential backoff
@app.task(bind=True, max_retries=5)
def unreliable_operation(self, data):
    try:
        return perform_operation(data)
    except Exception as exc:
        countdown = calculate_backoff(self.request.retries)
        raise self.retry(exc=exc, countdown=int(countdown))

# Bounded retry (fail after attempts)
@app.task(bind=True, max_retries=3)
def critical_operation(self, data):
    try:
        return perform_operation(data)
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            # Send to dead-letter queue
            deadletter_queue.put({"task": "critical_operation", "data": data})
            return {"status": "failed", "reason": str(exc)}
        raise self.retry(exc=exc, countdown=300)
```

**Circuit Breaker Pattern**:

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if datetime.now() - self.last_failure > timedelta(seconds=self.timeout):
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failures = 0
        self.state = 'CLOSED'

    def _on_failure(self):
        self.failures += 1
        self.last_failure = datetime.now()
        if self.failures >= self.failure_threshold:
            self.state = 'OPEN'

# Usage
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

@app.task(bind=True)
def external_api_call(self, data):
    try:
        return breaker.call(requests.get, 'https://api.example.com',
                           params=data)
    except Exception:
        # Fall back to cached/default response
        return cache.get(f"fallback:{data}")
```

**Idempotency**:

```python
# Idempotent task processing
@app.task(bind=True)
def process_payment(self, payment_data):
    # Generate idempotent key
    idempotent_key = f"payment:{payment_data['order_id']}:{payment_data['amount']}"

    # Check if already processed
    result = cache.get(idempotent_key)
    if result:
        return result

    try:
        # Process payment
        transaction = stripe.Charge.create(
            amount=payment_data['amount'],
            currency='usd',
            idempotency_key=idempotent_key  # Stripe's built-in idempotency
        )

        result = {
            'status': 'success',
            'transaction_id': transaction.id
        }

        # Cache result
        cache.setex(idempotent_key, 86400, json.dumps(result))

        return result
    except Exception as e:
        # Determine if retryable
        if is_retryable(e):
            raise self.retry(exc=e, countdown=60)
        else:
            return {'status': 'failed', 'reason': str(e)}
```

### Monitoring & Observability

**Key Metrics to Track**:

```
Queue Health:
├─ Queue depth (events waiting)
├─ Processing rate (events/sec)
├─ Error rate (%)
├─ Retry rate (%)
└─ Dead-letter queue size

Performance:
├─ Processing latency (p50, p99, max)
├─ End-to-end latency
├─ Worker utilization (%)
└─ Throughput per worker

Reliability:
├─ Task success rate
├─ Timeout occurrences
├─ Circuit breaker state changes
└─ Event loss (0 for durable systems)

Cost:
├─ Events processed
├─ Compute hours used
├─ Data transfer GB
└─ Cost per event
```

**Example Monitoring Setup (Python)**:

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
task_count = Counter(
    'tasks_processed_total',
    'Total tasks processed',
    ['task_name', 'status']
)

task_duration = Histogram(
    'task_duration_seconds',
    'Task processing duration',
    ['task_name']
)

queue_depth = Gauge(
    'queue_depth',
    'Current queue depth',
    ['queue_name']
)

@app.task(bind=True)
def monitored_task(self, data):
    start = time.time()
    try:
        result = process_data(data)
        task_count.labels(
            task_name='monitored_task',
            status='success'
        ).inc()
        return result
    except Exception as e:
        task_count.labels(
            task_name='monitored_task',
            status='failure'
        ).inc()
        raise
    finally:
        duration = time.time() - start
        task_duration.labels(
            task_name='monitored_task'
        ).observe(duration)
```

---

## Conclusion

**Quick Selection Guide**:

```
Choose BullMQ/Sidekiq if:
- Node.js or Ruby team
- Simple task queuing
- < 100K events/day

Choose Celery if:
- Python/Django shop
- Large data pipeline
- Familiar with async

Choose Temporal if:
- Long-running workflows
- Distributed transactions
- Willing to learn durable execution

Choose Inngest/Trigger.dev if:
- Serverless/FaaS focused
- Want zero ops burden
- < 1M events/month

Choose Kafka if:
- High throughput (>1M/day)
- Event replay/history needed
- Data pipeline / ETL
- Willing to manage complexity

Choose RabbitMQ if:
- Traditional microservices
- Complex routing needed
- Familiar with AMQP

Start small, measure, then migrate if needed. Most teams begin with simple Redis queues and graduate to Kafka/Temporal only when volume and complexity demand it.
```

---

## Related References
- [Caching, Message Queues & Background Jobs](./21-caching-queues.md) — Queue implementation details
- [Resilience Patterns](./52-resilience-patterns.md) — Reliability patterns for async systems
- [Observability & Distributed Tracing](./55-observability-tracing.md) — Monitoring async workflows
- [Backend Node.js/Bun/Deno](./04-backend-node.md) — Runtime considerations for workers
- [Real-Time Solutions](./16-realtime-websockets.md) — Real-time communication patterns

---

**Document Version**: 2.0
**Last Updated**: 2026-03-02
**Status**: Production-Ready
