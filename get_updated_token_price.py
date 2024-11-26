import requests
import json
from datetime import datetime

def get_pair_info(chain_id, pair_id):
    url = f'https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_id}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Vérifier si 'pairs' est dans la réponse et n'est pas None
        pairs = data.get('pairs')
        if pairs:
            pair = pairs[0]  # Comme nous demandons une seule paire, nous prenons le premier élément
            return pair
        else:
            print("Aucune donnée trouvée pour l'adresse de la paire fournie.")
            print("Réponse de l'API :", json.dumps(data, indent=4))
            return None

    except requests.exceptions.HTTPError as errh:
        print(f"Erreur HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Erreur de connexion: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Erreur de délai d'attente: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Erreur de requête: {err}")

def process_simulated_purchases():
    try:
        # Lire le fichier simulated_purchases.json
        with open('simulated_purchases.json', 'r') as f:
            simulated_purchases = json.load(f)
    except Exception as e:
        print(f"Erreur lors de la lecture de simulated_purchases.json: {e}")
        return

    results = []  # Pour stocker les résultats finaux
    total_purchase_amount = 0.0  # Montant total investi
    total_current_investment_value = 0.0  # Valeur actuelle totale des investissements

    for purchase in simulated_purchases:
        token_name = purchase.get('Token Name', 'Unknown')
        chain_id = purchase.get('Chain ID', '')
        pair_id = purchase.get('Full Hash 1', '')
        purchase_price = purchase.get('Purchase Price', 0.0)
        purchase_amount = purchase.get('Purchase Amount ($)', 0.0)
        amount_of_tokens = purchase.get('Amount of Tokens Purchased', 0.0)
        purchase_date = purchase.get('Purchase Date', '')
        
        if not chain_id or not pair_id:
            print(f"Skipping token '{token_name}' due to missing chain ID or pair ID.")
            continue

        print(f"Retrieving data for token '{token_name}' with chain ID '{chain_id}' and pair ID '{pair_id}'")
        pair_info = get_pair_info(chain_id, pair_id)
        if pair_info:
            # Récupérer le prix actuel
            current_price_usd = pair_info.get('priceUsd', 0.0)
            if current_price_usd == 'N/A' or current_price_usd == '':
                print(f"Le prix actuel pour le token '{token_name}' n'est pas disponible.")
                continue
            current_price_usd = float(current_price_usd)

            # Récupérer les informations supplémentaires
            liquidity_usd = pair_info.get('liquidity', {}).get('usd', 0.0)
            fdv = pair_info.get('fdv', 'N/A')
            volume_24h = pair_info.get('volume', {}).get('h24', 0.0)
            txns_24h_info = pair_info.get('txns', {}).get('h24', {})
            buys_24h = txns_24h_info.get('buys', 0)
            sells_24h = txns_24h_info.get('sells', 0)
            txns_24h = buys_24h + sells_24h

            # Convertir les valeurs en float si nécessaire
            liquidity_usd = float(liquidity_usd) if liquidity_usd not in ['N/A', ''] else 0.0
            volume_24h = float(volume_24h) if volume_24h not in ['N/A', ''] else 0.0
            buys_24h = int(buys_24h) if buys_24h not in ['N/A', ''] else 0
            sells_24h = int(sells_24h) if sells_24h not in ['N/A', ''] else 0
            txns_24h = int(txns_24h) if txns_24h not in ['N/A', ''] else 0
            fdv = float(fdv) if fdv not in ['N/A', ''] else 'N/A'

            # Calculer la valeur actuelle de l'investissement
            current_investment_value = amount_of_tokens * current_price_usd

            # Calculer le gain ou la perte en montant absolu
            profit_loss_amount = current_investment_value - purchase_amount

            # Calculer le gain ou la perte en pourcentage
            profit_loss_percentage = (profit_loss_amount / purchase_amount) * 100 if purchase_amount != 0 else 0

            # Accumuler les totaux
            total_purchase_amount += purchase_amount
            total_current_investment_value += current_investment_value

            # Préparer les résultats
            result = {
                "Token Name": token_name,
                "Chain ID": chain_id,
                "Pair ID": pair_id,
                "Purchase Date": purchase_date,
                "Purchase Price": purchase_price,
                "Current Price": current_price_usd,
                "Purchase Amount ($)": purchase_amount,
                "Current Investment Value ($)": current_investment_value,
                "Profit/Loss Amount ($)": profit_loss_amount,
                "Profit/Loss Percentage (%)": profit_loss_percentage,
                "Amount of Tokens Purchased": amount_of_tokens,
                "Liquidity USD": liquidity_usd,
                "Market Cap (FDV)": fdv,
                "Volume 24h": volume_24h,
                "Transactions 24h": txns_24h,
                "Buys 24h": buys_24h,
                "Sells 24h": sells_24h,
                "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            results.append(result)

            # Afficher les résultats pour ce token
            print(f"--- Résultats pour le token '{token_name}' ---")
            print(f"Acheté le : {purchase_date}")
            print(f"Prix d'achat : ${purchase_price}")
            print(f"Prix actuel : ${current_price_usd}")
            print(f"Montant investi : ${purchase_amount}")
            print(f"Valeur actuelle de l'investissement : ${current_investment_value:.4f}")
            if profit_loss_amount >= 0:
                print(f"Gain : ${profit_loss_amount:.4f} (+{profit_loss_percentage:.2f}%)")
            else:
                print(f"Perte : ${profit_loss_amount:.4f} ({profit_loss_percentage:.2f}%)")
            print(f"Liquidité (USD) : ${liquidity_usd}")
            print(f"Market Cap (FDV) : {fdv if fdv != 'N/A' else 'Non Disponible'}")
            print(f"Volume sur 24h : ${volume_24h}")
            print(f"Transactions sur 24h : {txns_24h} (Achats: {buys_24h}, Ventes: {sells_24h})")
            print("-" * 40)
        else:
            print(f"Les informations pour le token '{token_name}' n'ont pas pu être récupérées.")

    # Calculer le gain ou la perte total
    total_profit_loss_amount = total_current_investment_value - total_purchase_amount
    if total_purchase_amount != 0:
        total_profit_loss_percentage = (total_profit_loss_amount / total_purchase_amount) * 100
    else:
        total_profit_loss_percentage = 0

    # Afficher le gain ou la perte total
    print("\n=== Résultats Totaux ===")
    print(f"Montant total investi : ${total_purchase_amount}")
    print(f"Valeur totale actuelle des investissements : ${total_current_investment_value:.4f}")
    if total_profit_loss_amount >= 0:
        print(f"Gain total : ${total_profit_loss_amount:.4f} (+{total_profit_loss_percentage:.2f}%)")
    else:
        print(f"Perte totale : ${total_profit_loss_amount:.4f} ({total_profit_loss_percentage:.2f}%)")
    print("========================\n")

    # Enregistrer les résultats dans un fichier JSON
    if results:
        with open('purchase_results.json', 'w') as f:
            json.dump(results, f, indent=4)
        print("Les résultats ont été enregistrés dans 'purchase_results.json'.")

if __name__ == '__main__':
    process_simulated_purchases()
