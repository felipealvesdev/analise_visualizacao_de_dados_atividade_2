import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs("assets", exist_ok=True)

fig, ax = plt.subplots(figsize=(14, 3.5), facecolor='#0d47a1')
ax.set_facecolor('#0d47a1')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Faixa decorativa à esquerda
rect = patches.Rectangle((0, 0), 0.06, 1, color='#ffb300')
ax.add_patch(rect)

# Título principal
ax.text(0.5, 0.62, 'DESENROLA BRASIL',
        ha='center', va='center',
        fontsize=48, color='white', fontweight='bold',
        family='sans-serif')

# Subtítulo
ax.text(0.5, 0.28, 'Painel Analítico de Volume e Operações',
        ha='center', va='center',
        fontsize=20, color='#90caf9',
        style='italic')

# Rodapé
ax.text(0.98, 0.05, 'Análise e Visualização de Dados  •  CESAR School',
        ha='right', va='bottom',
        fontsize=10, color='#90caf9')

plt.tight_layout()
plt.savefig('assets/dashboard-cover.png', dpi=150,
            bbox_inches='tight', facecolor='#0d47a1')
plt.close()

print("✅ Banner gerado em assets/dashboard-cover.png")