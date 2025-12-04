// generate-sitemap.js
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
// import { posts } from './src/assets/data/articles.json'
import posts from './src/assets/data/articles.json' assert { type: 'json' };

// pour __dirname en ESM :
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const BASE_URL = 'https://jeremiecode.fr/projet/labo/babydose'

// 📅 Date du jour au format YYYY-MM-DD
const today = new Date().toISOString().split('T')[0]

const routes = [
  '/',
  '/calculateur',
  '/fonctionnalites',
  '/blog',
  '/politique-de-confidentialite'
].map(path => ({ path, lastmod: today }))

// 📝 Articles du blog : extraire la date et la transformer en format ISO
const blogRoutes = posts.map(post => {
  const rawDate = post.date // ex: "27 Mai 2025"
  const parsedDate = new Date(rawDate)
  const isoDate = isNaN(parsedDate) ? today : parsedDate.toISOString().split('T')[0]
  return {
    path: `/blog/${post.slug}`,
    lastmod: isoDate
  }
})

// 🧩 Fusionner tous les chemins
const allRoutes = [...routes, ...blogRoutes]

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
${allRoutes.map(({ path, lastmod }) => `
  <url>
    <loc>${BASE_URL}${path}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>${path === '/' ? '1.0' : '0.8'}</priority>
  </url>`).join('\n')}
</urlset>
`
fs.writeFileSync(path.resolve(__dirname, 'public/sitemap.xml'), xml)
console.log('✅ sitemap.xml généré avec succès')
