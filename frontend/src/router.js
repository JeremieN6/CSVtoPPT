import { createRouter, createWebHistory } from 'vue-router'
import UserProfilePage from './pages/UserProfilePage.vue'
import LandingPage from './pages/LandingPage.vue'
import ConvertisseurPage from './pages/ConvertisseurPage.vue'
import BypassPage from './pages/BypassPage.vue';
import FonctionnalitePage from './pages/FonctionnalitePage.vue'
import BlogPage from './pages/BlogPage.vue'
import BlogContentPage from './pages/BlogContentPage.vue'
import PolitiqueConfidentialitePage from './pages/PolitiqueConfidentialitePage.vue'
import ConnexionPage from './pages/ConnexionPage.vue'
import InscriptionPage from './pages/InscriptionPage.vue'
import Success from './pages/stripe/Success.vue'
import Cancel from './pages/stripe/Cancel.vue'

const routes = [
  { path: '/', component: LandingPage,
    meta: {
      title: 'CSVtoPPT | Home',
      description: 'Glissez un fichier CSV ou XLSX, lancez la génération et récupérez une présentation PowerPoint formatée automatiquement.'
    }
   },
  { path: '/convertisseur', component: ConvertisseurPage,
    meta: {
      title: 'CSVtoPPT | Convertisseur de fichier',
      description: 'Glissez un fichier CSV ou XLSX, lancez la génération et récupérez une présentation PowerPoint formatée automatiquement.'
    }
   },
  { path: '/fonctionnalites', component: FonctionnalitePage,
    meta: {
      title: 'CSVtoPPT | Fonctionnalités',
      description: 'Découvrez les fonctionnalités de CSVtoPPT : calcul de dose, unités compatibles, arrondis, historique et partage.'
    }
   },
   { path: '/blog', component: BlogPage,
    meta: {
      title: 'CSVtoPPT | Blog',
      description: 'Conseils et articles autour des bonnes pratiques concernant les fichiers csv et ppt.'
    }
   },
   { path: '/blog/:slug', name: 'BlogContent', component: BlogContentPage,
    meta: {
      title: 'CSVtoPPT | Article',
      description: 'Lecture d’un article du blog CSVtoPPT : informations et conseils autour de cette thématique..'
    }
   },
   { path: '/politique-de-confidentialite', component: PolitiqueConfidentialitePage,
    meta: {
      title: 'CSVtoPPT | Politique de confidentialité',
      description: 'En savoir plus sur la collecte, notre utilisation protection de vos données sur CSVtoPPT.'
    }
   },
   { path: '/connexion', component: ConnexionPage,
    meta: {
      title: 'CSVtoPPT | Connexion',
      description: 'Connectez-vous à votre compte CSVtoPPT.'
    }
   },
   { path: '/inscription', component: InscriptionPage,
    meta: {
      title: 'CSVtoPPT | Inscription',
      description: 'Créez votre compte CSVtoPPT et commencez à convertir vos fichiers.'
    }
   },
      { path: '/mon-compte', component: UserProfilePage,
    meta: {
      title: 'CSVtoPPT | Mon Compte',
      description: 'Mon espace personnel.'
    }
   },
   { path: '/success', component: Success,
    meta: {
      title: 'CSVtoPPT | Paiement réussi',
      description: 'Merci pour votre soutien ! Votre paiement a été confirmé et votre accès est activé.'
    }
   },
   { path: '/cancel', component: Cancel,
    meta: {
      title: 'CSVtoPPT | Paiement annulé',
      description: 'Le paiement a été annulé. Vous pouvez réessayer à tout moment depuis la page de souscription.'
    }
   },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router