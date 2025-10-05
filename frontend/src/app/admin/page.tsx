/**
 * Admin Index Page
 * 
 * Simple index page listing all available admin routes.
 */

export default function AdminPage() {
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#000',
      color: '#fff',
      fontFamily: 'var(--font-body)',
      padding: '2rem',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <h1 style={{
        fontSize: '2rem',
        fontWeight: '700',
        marginBottom: '3rem',
        textAlign: 'center'
      }}>
        Admin Panel
      </h1>
      
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem',
        alignItems: 'center'
      }}>
        <a 
          href="/admin/usage"
          style={{
            fontSize: '1.2rem',
            textDecoration: 'underline',
            color: '#fff'
          }}
        >
          Usage Dashboard
        </a>
        
        <a 
          href="/admin/database"
          style={{
            fontSize: '1.2rem',
            textDecoration: 'underline',
            color: '#fff'
          }}
        >
          Database Viewer
        </a>
      </div>
      
      <div style={{
        marginTop: '4rem',
        fontSize: '0.9rem',
        opacity: '0.6'
      }}>
        <a href="/" style={{ color: '#fff', textDecoration: 'underline' }}>
          ← Back to App
        </a>
      </div>
    </div>
  );
}
