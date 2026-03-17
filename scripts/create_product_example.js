// Example: create_product_example.js
// Usage:
// SHOPIFY_ADMIN_URL="https://your-shop.myshopify.com/admin/api/2024-10/graphql.json" \
// SHOPIFY_ADMIN_TOKEN="shpat_..." node scripts/create_product_example.js

const url = process.env.SHOPIFY_ADMIN_URL;
const token = process.env.SHOPIFY_ADMIN_TOKEN;

if (!url || !token) {
  console.error('Missing SHOPIFY_ADMIN_URL or SHOPIFY_ADMIN_TOKEN environment variables.');
  process.exit(1);
}

const mutation = `
mutation ProductCreateExample($product: ProductCreateInput!) {
  productCreate(product: $product) {
    product {
      id
      title
    }
    userErrors {
      field
      message
    }
  }
}
`;

const variables = {
  product: {
    title: 'MCP Test Product',
    status: 'ACTIVE',
    descriptionHtml: '<p>Created via Dev MCP test script</p>',
    vendor: 'Xtreme'
  }
};

async function main() {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
      },
      body: JSON.stringify({ query: mutation, variables })
    });

    const json = await res.json();
    if (json.errors) {
      console.error('GraphQL errors:', JSON.stringify(json.errors, null, 2));
      process.exit(1);
    }

    const payload = json.data.productCreate;
    if (payload.userErrors && payload.userErrors.length) {
      console.error('User errors:', JSON.stringify(payload.userErrors, null, 2));
    } else {
      console.log('Product created:', payload.product);
    }
  } catch (err) {
    console.error('Request failed:', err);
    process.exit(1);
  }
}

main();
