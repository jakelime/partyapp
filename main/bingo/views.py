# main/bingo/views.py
import json
import logging
import random

from accounts import models as accounts_models
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from main.custom_mixin import LoginRequiredMixinNopassword

from .models import BingoBoard, BingoSettings, winningNumber

lg = logging.getLogger("django")


class HomeView(LoginRequiredMixinNopassword, TemplateView):
    template_name = "home_template.html"


class SettingsView(TemplateView):
    template_name = "bingo/boardcontrol.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not BingoSettings.objects.exists():
            BingoSettings().save()

        settings = BingoSettings.objects.all().first()
        context["settings"] = settings

        return context

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        if "change" in request.POST:
            if not BingoSettings.objects.exists():
                BingoSettings().save()
            settings = BingoSettings.objects.all().first()

            if self.request.POST.get("start_num").strip():
                settings.start_num = self.request.POST.get("start_num").strip()
            if self.request.POST.get("end_num").strip():
                settings.end_num = self.request.POST.get("end_num").strip()
            if self.request.POST.get("dims").strip():
                settings.dims = self.request.POST.get("dims").strip()

            settings.save()

        if "reset" in request.POST:
            winningNumber.objects.all().delete()
            BingoBoard.objects.all().delete()
            all_players = accounts_models.CustomUser.objects.all()
            for player in all_players:
                board = BingoBoard()
                board.generateBoard()
                board.owner = player
                board.save()

        return redirect(reverse("bingo:settings"))


class PlayerView(LoginRequiredMixinNopassword, TemplateView):
    template_name = "bingo/playerview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.request.user.bingo_board
        context["board"] = board
        context["dims"] = len(board.board)
        context["dims_list"] = range(0, len(board.board))
        context["winning_numbers"] = list(
            winningNumber.objects.values_list("num", flat=True)
        )
        context["user"] = self.request.user
        return context


class WinningNumbersView(LoginRequiredMixinNopassword, TemplateView):
    template_name = "bingo/projector.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the 7 latest winning numbers
        latest_winning_numbers = winningNumber.objects.all()[:7]

        # Put them into context as num1, num2, ..., num7
        for i, winning_number_obj in enumerate(latest_winning_numbers):
            context[f"num{i+1}"] = winning_number_obj.num

        # Optional: If you want to handle cases where there are less than 7 numbers
        # for i in range(len(latest_winning_numbers), 7):
        #     context[f'num{i+1}'] = None # Or some default value like 0 or an empty string

        # print("Context data:", context) # For debugging, check your server console

        return context


class GameMasterView(TemplateView):
    template_name = "bingo/gmview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # These are retrieved from URL parameters when a GET request comes in
        context["period"] = kwargs.get("period", 30)  # Default to 10 if not in URL
        context["toggle_state"] = kwargs.get("toggle_state", False)  # Default to False
        context["winning_numbers"] = list(
            winningNumber.objects.values_list("num", flat=True)
        )

        winners = BingoBoard.objects.all().filter(is_winner=True)
        context["winners"] = winners
        context["num_winners"] = len(winners)
        context["num_players"] = accounts_models.CustomUser.objects.all().count()
        context["num_drawn"] = len(
            list(winningNumber.objects.values_list("num", flat=True))
        )

        print(
            f"GET Request - Period: {context['period']}, Toggle State: {context['toggle_state']}"
        )
        return context

    # Handle POST requests from your JavaScript fetch
    def post(self, request, *args, **kwargs):
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            period = data.get("period")
            toggle_state = data.get("toggle_state")
            draw = data.get("draw")

            if draw:
                if not BingoSettings.objects.exists():
                    BingoSettings().save()

                settings = BingoSettings.objects.all().first()

                if (
                    winningNumber.objects.all().count()
                    == settings.end_num + 1 - settings.start_num
                ):
                    return JsonResponse({"error": "out of numbers"}, status=500)

                existing_winning_numbers = winningNumber.objects.values_list(
                    "num", flat=True
                )
                new_winning_number = random.randint(
                    settings.start_num, settings.end_num + 1
                )  # Assuming Bingo numbers are 1-75

                # Keep generating until we find a number that's not already a winner
                while new_winning_number in existing_winning_numbers:
                    new_winning_number = random.randint(
                        settings.start_num, settings.end_num + 1
                    )

                new_winning_number_obj = winningNumber(num=new_winning_number)
                new_winning_number_obj.save()

                # Get the list of all current winning numbers
                current_winning_numbers = list(
                    winningNumber.objects.values_list("num", flat=True)
                )

                # Query all existing Bingo boards
                all_boards = BingoBoard.objects.all()

                # Iterate through each board and call validate_board
                for board in all_boards:
                    validated_board = board.validate_board(
                        winning_numbers=current_winning_numbers
                    )
                    validated_board.save()  # Save the updated is_winner status

                winning_boards = BingoBoard.objects.all().filter(is_winner=True)
                print(winning_boards)

            # ------------------------------------
            # Construct the URL for redirection, including the parameters
            # Use the URL pattern name that expects these parameters
            redirect_url = reverse(
                "bingo:game_master_with_params",  # Use the namespaced URL name
                kwargs={"period": period, "toggle_state": toggle_state},
            )

            # Redirect back to the same page with the received parameters
            return redirect(redirect_url)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)
